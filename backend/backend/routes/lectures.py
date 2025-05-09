from typing import Optional, Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from database.database import get_db
from models import Lecture, ChatMessage, Chat, RelevantContent, StudySearchResult
from routes.chats import ChatResponse
from .relevant_content import search_study_content

router = APIRouter()


class LectureRequest(BaseModel):
    week_id: int
    sequence_no: int
    name: str
    type: str  # "Video" or "Assignment"
    url: Optional[HttpUrl] = None  # Only for videos
    video_id: Optional[str] = None
    content: Optional[Dict[str, Any]] = None  # Only for assignments


class LectureResponse(LectureRequest):
    id: int
    created_at: str

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            week_id=obj.week_id,
            sequence_no=obj.sequence_no,
            name=obj.name,
            type=obj.type,
            url=obj.url,
            video_id=obj.video_id,
            content=obj.content,
            created_at=obj.created_at.isoformat()  # ✅ Convert datetime to string
        )

    class Config:
        from_attributes = True


@router.get("/", response_model=List[LectureResponse])
def get_lectures(week_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Lecture)

    if week_id:
        query = query.filter(Lecture.week_id == week_id)

    lectures = query.order_by(Lecture.week_id, Lecture.sequence_no).all()

    if not lectures:
        raise HTTPException(status_code=404, detail="No lectures found")

    return [LectureResponse.from_orm(lecture) for lecture in lectures]


@router.post("/", response_model=LectureResponse)
def create_lecture(request: LectureRequest, db: Session = Depends(get_db)):
    new_lecture = Lecture(
        week_id=request.week_id,
        sequence_no=request.sequence_no,
        name=request.name,
        type=request.type,
        url=request.url,
        content=request.content,
    )

    db.add(new_lecture)
    db.commit()
    db.refresh(new_lecture)

    return new_lecture


@router.get("/{lecture_id}/chats", response_model=List[ChatResponse])
def get_chat_history_for_lecture(lecture_id: int, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(ChatMessage).join(Chat).options(
        joinedload(ChatMessage.relevant_content)
    ).filter(Chat.lecture_id == lecture_id)

    if user_id:
        query = query.filter(Chat.user_id == user_id)

    messages = query.order_by(ChatMessage.created_at).all()

    if not messages:
        raise HTTPException(status_code=404, detail="No chat history found for this lecture")

    return messages
