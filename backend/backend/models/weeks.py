from sqlalchemy import BigInteger, Column, TIMESTAMP, func, Text, ForeignKey

from models.base import Base


class Week(Base):
    __tablename__ = "weeks"
    __table_args__ = {"schema": "public"}  # Explicitly set the schema

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    name = Column(Text, nullable=True)
    subject_id = Column(BigInteger, ForeignKey("public.subjects.id"), nullable=False)

    def __repr__(self):
        return f"<Week(id={self.id}, name={self.name}, subject_id={self.subject_id})>"
