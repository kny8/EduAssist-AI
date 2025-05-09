from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models import Assignment
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

router = APIRouter()


class AssignmentRequest(BaseModel):
    week_id: int
    sequence_no: int
    name: str
    content: Dict[str, Any]


class AssignmentResponse(AssignmentRequest):
    id: int
    created_at: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[AssignmentResponse])
def get_assignments(week_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Assignment)

    if week_id:
        query = query.filter(Assignment.week_id == week_id)

    assignments = query.order_by(Assignment.week_id, Assignment.sequence_no).all()

    if not assignments:
        raise HTTPException(status_code=404, detail="No assignments found")

    return assignments


@router.post("/", response_model=AssignmentResponse)
def create_assignment(request: AssignmentRequest, db: Session = Depends(get_db)):
    new_assignment = Assignment(
        week_id=request.week_id,
        sequence_no=request.sequence_no,
        name=request.name,
        content=request.content,
    )

    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    return new_assignment
