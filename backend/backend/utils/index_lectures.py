from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from database.database import SessionLocal
from models import Lecture
import yt_dlp
import whisper
import os
from pydub import AudioSegment

# ✅ Define a persistent storage path
CHROMA_DB_PATH = "chroma_db"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
# ✅ Load HuggingFace embeddings
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

# Initialize Whisper model on CPU
whisper_model = whisper.load_model("small", device="cpu")


# def download_youtube_audio(youtube_url: str, output_path="downloads/audio.mp3"):
#     """
#     Downloads audio from a YouTube video.
#     """
#     ydl_opts = {
#         'format': 'bestaudio/best',
#         'outtmpl': output_path,
#         'postprocessors': [{
#             'key': 'FFmpegExtractAudio',
#             'preferredcodec': 'mp3',
#             'preferredquality': '192',
#         }],
#     }
#
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         ydl.download([youtube_url])
#
#     return output_path + '.mp3'
def download_youtube_audio(youtube_url: str, output_path="downloads/audio.mp3"):
    """
    Downloads audio from a YouTube video if not already downloaded.
    """
    output_file = output_path + ".mp3"
    if os.path.exists(output_file):
        print(f"📁 Audio already downloaded at: {output_file}")
        return output_file

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    return output_file


def transcribe_audio(audio_path: str):
    """
    Transcribes audio to text using Whisper and returns text with timestamps.
    """
    result = whisper_model.transcribe(audio_path, fp16=False)

    transcript_chunks = []
    for segment in result["segments"]:
        start_time = round(segment["start"], 2)
        end_time = round(segment["end"], 2)
        text = segment["text"]

        transcript_chunks.append({
            "start_time": start_time,
            "end_time": end_time,
            "text": text
        })

    return transcript_chunks


def process_youtube_video(youtube_url: str, name='1'):
    """
    Downloads and transcribes a YouTube video, returning text chunks with timestamps.
    """
    # Create downloads directory if it doesn't exist
    os.makedirs("downloads", exist_ok=True)

    audio_path = download_youtube_audio(youtube_url, f"downloads/lecture_{name}")
    transcript_chunks = transcribe_audio(audio_path)
    # os.remove(audio_path)  # Clean up the audio file after processing

    return transcript_chunks


def index_lecture_video(lecture_id: int, youtube_url: str, reindex: bool = False):
    """
    Transcribes a YouTube video and indexes the text with timestamps into ChromaDB.
    """
    print(f"📌 Checking lecture {lecture_id} for indexing...")

    # Initialize vector store
    vectorstore = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings)

    # 🔹 Check if the lecture is already indexed (based on first transcript chunk)
    existing_docs = vectorstore.get(["{}_0".format(lecture_id)])

    if existing_docs["documents"] and not reindex:
        print(f"✅ Lecture {lecture_id} is already indexed. Skipping...")
        return
    else:
        vectorstore.delete(where={"lecture_id": lecture_id})

    print(f"📌 Indexing lecture {lecture_id}...")

    # 🔹 Get transcript with timestamps
    transcript_chunks = process_youtube_video(youtube_url, name=str(lecture_id))

    # Prepare data for bulk insertion
    docs = []
    metadatas = []
    ids = []

    for chunk in transcript_chunks:
        docs.append(chunk["text"])
        metadatas.append({
            "lecture_id": lecture_id,
            "text": chunk["text"],
            "start_time": chunk["start_time"],
            "end_time": chunk["end_time"],
            "youtube_url": youtube_url
        })
        ids.append(f"{lecture_id}_{chunk['start_time']}")  # Unique ID

    # 🔹 Add documents to ChromaDB
    vectorstore.add_texts(texts=docs, metadatas=metadatas, ids=ids)

    print(f"✅ Video lecture {lecture_id} indexed successfully!")


def index_all_lectures():
    """
    Index all video lectures in the database.
    """
    reindex = True
    # Initialize DB session
    db = SessionLocal()
    try:
        lectures = db.query(Lecture).filter(Lecture.type == 'Video').all()
        # lectures = [lectures[0]]

        for lecture in lectures:
            if lecture.url is not None:
                index_lecture_video(lecture_id=lecture.id, youtube_url=lecture.url, reindex=reindex)

        print("✅ All lectures indexed successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    index_all_lectures()
