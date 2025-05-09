from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.database import get_db
from models import Subject, User, UserSubject, Week
from routes.weeks import WeekResponse
from utils.auth import get_current_user

router = APIRouter()


class Message(BaseModel):
    message: str


class SubjectRequest(BaseModel):
    name: str


@router.post("/", response_model=Message)
def create_subject(request: SubjectRequest, db: Session = Depends(get_db)):
    subject = Subject(name=request.name)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return {"message": "Subject created successfully"}


@router.get("/", response_model=List[SubjectRequest])
def get_subjects(db: Session = Depends(get_db)):
    subjects = db.query(Subject).all()
    return subjects


@router.get("/{subject_id}", response_model=SubjectRequest)
def get_subjects(subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()

    return subject


@router.get("/{subject_id}/weeks", response_model=List[WeekResponse])
def get_weeks(subject_id: int, db: Session = Depends(get_db)):
    weeks = db.query(Week).filter(Week.subject_id == subject_id).all()

    if not weeks:
        raise HTTPException(status_code=404, detail="No weeks found for this subject")

    # return [{"week_id": week.id, "name": week.name} for week in weeks]
    return weeks


class UserSubjectRequest(BaseModel):
    user_id: int
    subject_id: int


@router.post("/user-subjects/", response_model=Message)
def assign_subject_to_user(request: UserSubjectRequest, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if subject exists
    subject = db.query(Subject).filter(Subject.id == request.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # Assign subject to user
    user_subject = UserSubject(user_id=request.user_id, subject_id=request.subject_id)
    db.add(user_subject)
    db.commit()
    db.refresh(user_subject)

    return {"message": "User assigned to subject successfully"}


@router.get("/user-subjects/{user_id}", response_model=List[UserSubjectRequest])
def get_user_subjects(user_id: int, db: Session = Depends(get_db)):
    user_subjects = db.query(UserSubject).filter(UserSubject.user_id == user_id).all()

    if not user_subjects:
        raise HTTPException(status_code=404, detail="No subjects found for this user")

    subjects = db.query(Subject).filter(Subject.id.in_([us.subject_id for us in user_subjects])).all()
    return [{"subject_id": s.id, "name": s.name} for s in subjects]
