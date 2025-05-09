from sqlalchemy import Column, BigInteger, Text, ForeignKey, TIMESTAMP, func, Boolean
from sqlalchemy.orm import relationship
from models.base import Base


class Chat(Base):
    __tablename__ = "chats"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("public.users.id"), nullable=False)  # Links to a user
    lecture_id = Column(BigInteger, ForeignKey("public.lectures.id"), nullable=False)  # Links to a lecture
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)  # Timestamp

    # Add relationship
    # relevant_content = relationship("RelevantContent", back_populates="chat")
    # messages = relationship("ChatMessage", backref="chat")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, ForeignKey("public.chats.id"), nullable=False)  # Groups messages
    sender = Column(Text, nullable=False)  # "user" or "ai"
    message = Column(Text, nullable=False)  # Message content
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    is_read = Column(Boolean, default=False)  # Tracks if user has seen AI's response
    chat = relationship("Chat", backref="chat_messages")
