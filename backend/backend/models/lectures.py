from sqlalchemy import Column, BigInteger, TIMESTAMP, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from models.base import Base
from sqlalchemy.orm import relationship


class Lecture(Base):
    __tablename__ = "lectures"
    __table_args__ = {"schema": "public"}  # Explicit schema

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    week_id = Column(BigInteger, ForeignKey("public.weeks.id"), nullable=False)
    sequence_no = Column(BigInteger, nullable=True)
    name = Column(Text, nullable=False)
    type = Column(Text, nullable=False)  # "Video" or "Assignment"
    url = Column(Text, nullable=True)  # For videos
    content = Column(JSONB, nullable=True)  # For assignments (JSON format)
    video_id = Column(Text, nullable=True)  # For videos

    def __repr__(self):
        return f"<Lecture(id={self.id}, name={self.name}, type={self.type}, sequence_no={self.sequence_no})>"


class RelevantContent(Base):
    __tablename__ = "relevant_content"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, ForeignKey("public.chats.id"), nullable=False)
    chat_message_id = Column(BigInteger, ForeignKey("public.chat_messages.id"), nullable=False)
    lecture_id = Column(BigInteger, ForeignKey("public.lectures.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("public.users.id"), nullable=True)
    content_type = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    url = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Add relationships
    chat = relationship("Chat", backref="relevant_content")
    chat_message = relationship("ChatMessage", backref="relevant_content")


class StudySearchResult(Base):
    __tablename__ = "study_search_results"
    __table_args__ = {"schema": "public"}
    id = Column(BigInteger, primary_key=True, index=True)
    lecture_id = Column(BigInteger, ForeignKey("public.lectures.id", ondelete="CASCADE"), nullable=False)
    query = Column(Text, index=True)
    context = Column(Text, nullable=True)
    title = Column(Text)
    link = Column(Text)
    snippet = Column(Text)
    source = Column(Text)
    date = Column(TIMESTAMP(timezone=True), default=func.now(), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    last_accessed = Column(TIMESTAMP(timezone=True), default=func.now(), nullable=True)

    # Relationship with CodeExercise
    lecture = relationship("Lecture", backref="search_results")


# class Week(Base):
#     __tablename__ = "weeks"
#
#     id = Column(BigInteger, primary_key=True, index=True)
#     name = Column(Text, nullable=False)
#     subject_id = Column(BigInteger, ForeignKey("public.subjects.id"), nullable=False)
#     order = Column(BigInteger, nullable=False)
#     # subject = relationship("Subject", back_populates="weeks")
#     # lectures = relationship("Lecture", back_populates="week", cascade="all, delete-orphan")
#     # quizzes = relationship("Quiz", back_populates="week", cascade="all, delete-orphan")
