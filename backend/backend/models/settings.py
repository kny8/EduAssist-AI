from sqlalchemy import Column, BigInteger, Text, Boolean, Float, TIMESTAMP, func
from models.base import Base


class Settings(Base):
    __tablename__ = "settings"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    api_base_url = Column(Text, nullable=True)  # API Base URL
    api_key = Column(Text, nullable=True)  # API Key (encrypted in production)
    model_name = Column(Text, nullable=False, default="gpt-4")  # AI Model
    temperature = Column(Float, nullable=False, default=0.7)  # AI Randomness
    max_tokens = Column(BigInteger, nullable=False, default=1000)  # Token limit
    dark_mode = Column(Boolean, default=False)  # Dark mode preference
    notifications_enabled = Column(Boolean, default=True)  # Enable notifications
    response_speed = Column(Float, nullable=False, default=1.0)  # Response speed factor
    streaming_mode = Column(Boolean, default=False)  # Enable streaming mode
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
