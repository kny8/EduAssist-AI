from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models import UserProfile
from models.users import User
from pydantic import BaseModel, HttpUrl

router = APIRouter()


# ✅ Profile Request Model (Used for Updating)
class UserProfileRequest(BaseModel):
    bio: Optional[str] = None
    profile_picture: Optional[HttpUrl] = None
    dark_mode: Optional[bool] = None
    notifications_enabled: Optional[bool] = None


# ✅ Profile Response Model (Used for Fetching)
class UserProfileResponse(UserProfileRequest):
    user_id: int
    created_at: str

    class Config:
        from_attributes = True


# ✅ GET: Fetch User Profile
@router.get("/profile/{user_id}", response_model=UserProfileResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    return profile


# ✅ POST: Create or Update User Profile
@router.post("/profile/{user_id}", response_model=UserProfileResponse)
def update_user_profile(user_id: int, request: UserProfileRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    if profile:
        # Update existing profile
        if request.bio:
            profile.bio = request.bio
        if request.profile_picture:
            profile.profile_picture = str(request.profile_picture)
        if request.dark_mode is not None:
            profile.dark_mode = request.dark_mode
        if request.notifications_enabled is not None:
            profile.notifications_enabled = request.notifications_enabled
    else:
        # Create new profile
        profile = UserProfile(
            user_id=user_id,
            bio=request.bio,
            profile_picture=str(request.profile_picture) if request.profile_picture else None,
            dark_mode=request.dark_mode if request.dark_mode is not None else False,
            notifications_enabled=request.notifications_enabled if request.notifications_enabled is not None else True
        )
        db.add(profile)

    db.commit()
    db.refresh(profile)

    return profile
