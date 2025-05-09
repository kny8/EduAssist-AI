from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models import Video
from pydantic import BaseModel, HttpUrl
from typing import List, Optional

router = APIRouter()


class VideoRequest(BaseModel):
    week_id: int
    sequence_no: int
    name: str
    url: HttpUrl


class VideoResponse(VideoRequest):
    id: int
    created_at: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[VideoResponse])
def get_videos(week_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Video)

    if week_id:
        query = query.filter(Video.week_id == week_id)

    videos = query.order_by(Video.week_id, Video.sequence_no).all()

    if not videos:
        raise HTTPException(status_code=404, detail="No videos found")

    return videos


@router.post("/", response_model=VideoResponse)
def create_video(request: VideoRequest, db: Session = Depends(get_db)):
    new_video = Video(
        week_id=request.week_id,
        sequence_no=request.sequence_no,
        name=request.name,
        url=request.url,
    )

    db.add(new_video)
    db.commit()
    db.refresh(new_video)

    return new_video
