import datetime

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
import jwt
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database.database import get_db
from models import User
from utils.auth import SECRET_KEY, get_current_user

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Fetch user by email
    user = db.query(User).filter(User.email == request.email).first()

    # If user not found or password doesn't match
    if not user or not bcrypt.checkpw(request.password.encode(), user.password.encode()):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generate JWT token
    payload = {
        "sub": str(user.id),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # Token expiry
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return {"access_token": token, "token_type": "bearer"}


# Pydantic model for registering a new user
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str


@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password
    hashed_password = bcrypt.hashpw(request.password.encode(), bcrypt.gensalt()).decode()

    # Create a new user
    new_user = User(
        email=request.email,
        password=hashed_password,
        name=request.name,
        role=request.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "user_id": new_user.id}


@router.get("/me")
def get_me(db: Session = Depends(get_db), currentUser=Depends(get_current_user)):
    print(currentUser)
    return db.query(User).filter(User.id == currentUser).first()
