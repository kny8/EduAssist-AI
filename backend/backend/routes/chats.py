from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from database.chroma_db import get_chroma_collection
from database.database import get_db
from models import Chat, ChatMessage, RelevantContent

from pydantic import BaseModel
from typing import List, Optional
import datetime

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain_huggingface import HuggingFacePipeline

from utils.index_lectures import CHROMA_DB_PATH

router = APIRouter()


class ChatRequest(BaseModel):
    lecture_id: int
    user_id: int
    message: str
    one: bool = False


class RelevantContentResponse(BaseModel):
    id: int
    content_type: str
    title: str
    description: Optional[str]
    url: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    id: int
    chat_id: int
    sender: str
    message: str
    created_at: datetime.datetime
    relevant_content: Optional[List[RelevantContentResponse]] = None

    class Config:
        from_attributes = True


@router.get("/{lecture_id}", response_model=List[ChatResponse])
def get_chat_history(lecture_id: int, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(ChatMessage).join(Chat).options(
        joinedload(ChatMessage.relevant_content)
    ).filter(Chat.lecture_id == lecture_id)

    if user_id:
        query = query.filter(Chat.user_id == user_id)

    messages = query.order_by(ChatMessage.created_at).all()

    if not messages:
        raise HTTPException(status_code=404, detail="No chat history found for this lecture")

    return messages
    # query = db.query(ChatMessage).join(Chat).filter(Chat.lecture_id == lecture_id)
    #
    # if user_id:
    #     query = query.filter(Chat.user_id == user_id)
    #
    # messages = query.order_by(ChatMessage.created_at).all()
    #
    # if not messages:
    #     raise HTTPException(status_code=404, detail="No chat history found for this lecture")
    #
    # # Get relevant content for each AI message
    # for message in messages:
    #     if message.sender == "ai":
    #         relevant_content = db.query(RelevantContent).filter(and_(
    #             RelevantContent.lecture_id == lecture_id,
    #
    #         )
    #         ).all()
    #         message.relevant_content = relevant_content
    #
    # return messages


@router.post("/", response_model=ChatResponse)
def send_message(request: ChatRequest, db: Session = Depends(get_db)):
    # Check if a conversation exists for this user and lecture
    conversation = db.query(Chat).filter(
        Chat.lecture_id == request.lecture_id,
        Chat.user_id == request.user_id
    ).first()

    if not conversation:
        conversation = Chat(user_id=request.user_id, lecture_id=request.lecture_id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    try:
        # Store user message first
        user_message = ChatMessage(
            chat_id=conversation.id,
            sender="user",
            message=request.message
        )
        db.add(user_message)
        db.flush()

        # Get AI response using RAG
        if request.one:
            ai_response_dict = search_one_lecture(request.message, request.lecture_id)
        else:
            ai_response_dict = search_all_lectures(request.message)

        # Store AI response
        ai_message = ChatMessage(
            chat_id=conversation.id,
            sender="ai",
            message=ai_response_dict.get("message", "I apologize, I couldn't find relevant information.")
        )
        db.add(ai_message)
        db.flush()

        # Store relevant content with references to both chat and message
        relevant_content_list = []
        if "results" in ai_response_dict and ai_response_dict["results"]:
            results = ai_response_dict["results"]
            for result in results:
                timestamp = int(float(result['timestamp']))
                relevant_content = RelevantContent(
                    chat_id=conversation.id,
                    chat_message_id=ai_message.id,
                    lecture_id=result['lecture_id'],
                    user_id=request.user_id,
                    content_type="Video",
                    title=f"Lecture {result['lecture_id']} - Relevant Segment",
                    description=result['text'][:150] + "...",
                    url=f"?t={timestamp}"
                )
                db.add(relevant_content)
                relevant_content_list.append(relevant_content)

        db.commit()

        ai_message.relevant_content = relevant_content_list
        return ai_message

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Initialize embeddings model
model_name = "sentence-transformers/all-MiniLM-L6-v2"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

# Initialize LLM
llm_name = "mistralai/Mistral-7B-Instruct-v0.1"
tokenizer = AutoTokenizer.from_pretrained(llm_name)
model = AutoModelForCausalLM.from_pretrained(
    llm_name,
    torch_dtype="auto",
    device_map="auto"
)
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=256
)
llm = HuggingFacePipeline(pipeline=pipe)


def search_one_lecture(message: str, lecture_id: int):
    """
    Retrieves relevant content from a specific lecture and generates an AI response using RAG.
    """
    print(f"📌 Searching **Lecture {lecture_id}** for relevant content...")

    try:
        # ✅ Load Chroma vector store
        vectorstore = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings)

        # ✅ Retrieve relevant documents **only for this lecture**
        results = vectorstore.similarity_search(
            message, k=1, filter={"lecture_id": lecture_id}
        )

        if not results:
            return {"message": "⚠️ No relevant content found in this lecture."}

        # ✅ Extract metadata & transcript
        best_match = results[0].metadata
        timestamp = best_match["start_time"]
        youtube_url = best_match["youtube_url"]
        lecture_text = results[0].page_content

        # ✅ Format query for LLM
        context = f"""
        Lecture {lecture_id}, segment at {timestamp}s:
        {lecture_text}

        Question: {message}
        Answer:"""

        response = llm.invoke(context)

        return {
            "message": "🔍 **Found Relevant Content:**",
            "results": [{
                "lecture_id": lecture_id,
                "timestamp": timestamp,
                "youtube_url": youtube_url,
                "text": lecture_text,
                "ai_response": response.strip()
            }]
        }

    except Exception as e:
        return {"message": f"❌ An error occurred: {str(e)}"}


def search_all_lectures(query: str, k: int = 5):
    """
    Searches across all indexed lectures for the most relevant transcript chunks.
    """
    vectorstore = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings)

    # ✅ Perform similarity search across all lectures
    results = vectorstore.similarity_search(query, k=k)

    if not results:
        return {"message": "⚠️ No relevant content found across all lectures."}

    response_list = []

    for doc in results:
        metadata = doc.metadata
        lecture_id = metadata["lecture_id"]
        youtube_url = metadata["youtube_url"]
        timestamp = metadata["start_time"]
        # text = metadata["text"]
        text = doc.page_content
        # ✅ Format query for LLM
        context = f"""
        Lecture {lecture_id}, segment at {timestamp}s:
        {text}

        Question: {query}
        Answer:"""

        response = llm.invoke(context)

        response_list.append({
            "lecture_id": lecture_id,
            "timestamp": timestamp,
            "youtube_url": youtube_url,
            "text": text,
            "ai_response": response.strip()
        })

    return {
        "message": "🔍 **Found Relevant Content:**",
        "results": response_list
    }


# Add a new endpoint to get relevant content by chat
@router.get("/chat/{chat_id}/relevant-content")
def get_chat_relevant_content(chat_id: int, db: Session = Depends(get_db)):
    return db.query(RelevantContent).filter(
        RelevantContent.chat_id == chat_id
    ).order_by(RelevantContent.created_at.desc()).all()


# Update the latest relevant content endpoint
@router.get("/latest-relevant-content/{lecture_id}")
def get_latest_relevant_content(lecture_id: int, user_id: int, db: Session = Depends(get_db)):
    # Now we can query directly through RelevantContent
    latest_content = db.query(RelevantContent).join(Chat).filter(
        Chat.lecture_id == lecture_id,
        Chat.user_id == user_id
    ).order_by(RelevantContent.created_at.desc()).first()

    return latest_content if latest_content else []
