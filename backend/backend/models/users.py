from sqlalchemy import BigInteger, Column, TIMESTAMP, func, Text, ForeignKey, Boolean

from models.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}  # Explicitly set the schema

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    email = Column(Text, unique=True, nullable=True)  # Make email unique if needed
    password = Column(Text, nullable=True)  # Store hashed password
    name = Column(Text, nullable=True)
    role = Column(Text, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name}, role={self.role})>"


class UserProfile(Base):
    __tablename__ = "user_profiles"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("public.users.id", ondelete="CASCADE"), unique=True,
                     nullable=False)
    bio = Column(Text, nullable=True)
    profile_picture = Column(Text, nullable=True)
    dark_mode = Column(Boolean, default=False)
    notifications_enabled = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
