from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models.settings import Settings
from pydantic import BaseModel, HttpUrl

router = APIRouter()


class SettingsRequest(BaseModel):
    api_base_url: Optional[HttpUrl] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    dark_mode: Optional[bool] = None
    notifications_enabled: Optional[bool] = None
    response_speed: Optional[float] = None
    streaming_mode: Optional[bool] = None


class SettingsResponse(SettingsRequest):
    id: int
    created_at: str

    class Config:
        from_attributes = True


@router.get("/settings", response_model=SettingsResponse)
def get_system_settings(db: Session = Depends(get_db)):
    settings = db.query(Settings).first()

    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    return settings


@router.post("/settings", response_model=SettingsResponse)
def update_system_settings(request: SettingsRequest, db: Session = Depends(get_db)):
    settings = db.query(Settings).first()

    if not settings:
        settings = Settings()
        db.add(settings)

    # Update fields if provided
    if request.api_base_url:
        settings.api_base_url = str(request.api_base_url)
    if request.api_key:
        settings.api_key = request.api_key
    if request.model_name:
        settings.model_name = request.model_name
    if request.temperature is not None:
        settings.temperature = request.temperature
    if request.max_tokens is not None:
        settings.max_tokens = request.max_tokens
    if request.dark_mode is not None:
        settings.dark_mode = request.dark_mode
    if request.notifications_enabled is not None:
        settings.notifications_enabled = request.notifications_enabled
    if request.response_speed is not None:
        settings.response_speed = request.response_speed
    if request.streaming_mode is not None:
        settings.streaming_mode = request.streaming_mode

    db.commit()
    db.refresh(settings)

    return settings
