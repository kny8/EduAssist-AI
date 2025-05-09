from sqlalchemy import Column, BigInteger, TIMESTAMP, Text, func, ForeignKey

from models.base import Base


class Subject(Base):
    __tablename__ = "subjects"
    __table_args__ = {"schema": "public"}  # Explicitly set the schema

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    name = Column(Text, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id},  name={self.name} )>"


class UserSubject(Base):
    __tablename__ = "user_subjects"
    __table_args__ = {"schema": "public"}  # Explicitly set the schema

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    user_id = Column(BigInteger, ForeignKey("public.users.id"), nullable=False)
    subject_id = Column(BigInteger, ForeignKey("public.subjects.id"), nullable=False)
