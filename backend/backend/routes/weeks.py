from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.database import get_db
from models import Subject, Lecture
from models.weeks import Week
from routes.lectures import LectureResponse

router = APIRouter()


class WeekRequest(BaseModel):
    name: str
    subject_id: int


class WeekResponse(WeekRequest):
    id: int


@router.post("/", response_model=dict)
def create_week(request: WeekRequest, db: Session = Depends(get_db)):
    # Check if subject exists
    subject = db.query(Subject).filter(Subject.id == request.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # Create a new week under the subject
    week = Week(name=request.name, subject_id=request.subject_id)
    db.add(week)
    db.commit()
    db.refresh(week)

    return {"message": "Week created successfully", "week_id": week.id}


@router.get("/{week_id}", response_model=WeekResponse)
def get_weeks_for_subject(week_id: int, db: Session = Depends(get_db)):
    # Get all weeks for the given subject
    week = db.query(Week).filter(Week.id == week_id).first()
    return week
    # if not weeks:
    #     raise HTTPException(status_code=404, detail="No weeks found for this subject")
    #
    # return [{"week_id": week.id, "name": week.name} for week in weeks]


@router.get("/{week_id}/lectures", response_model=List[LectureResponse])
def get_weeks_for_subject(week_id: int, db: Session = Depends(get_db)):
    # Get all weeks for the given subject
    lectures = db.query(Lecture).filter(Lecture.week_id == week_id).order_by(Lecture.sequence_no).all()
    return [LectureResponse.from_orm(lecture) for lecture in lectures]
