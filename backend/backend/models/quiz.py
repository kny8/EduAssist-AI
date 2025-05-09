from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

from models.base import Base


class Quiz(Base):
    __tablename__ = "quizzes"
    __table_args__ = {"schema": "public"}
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    after = Column(Integer, ForeignKey("public.weeks.id"), nullable=False)

    # Relationship with Week
    week = relationship("Week", backref="quizzes")
