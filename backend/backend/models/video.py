from sqlalchemy import Column, BigInteger, TIMESTAMP, Text, ForeignKey, func
from models.base import Base


class Video(Base):
    __tablename__ = "videos"
    __table_args__ = {"schema": "public"}  # Explicitly set the schema

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    name = Column(Text, nullable=True)
    week_id = Column(BigInteger, ForeignKey("public.weeks.id"), nullable=False)
    sequence_no = Column(BigInteger, nullable=True)
    url = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Video(id={self.id}, name={self.name}, sequence_no={self.sequence_no}, url={self.url})>"