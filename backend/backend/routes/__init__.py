from fastapi import APIRouter

from . import (
    auth,
    subjects,
    weeks,
    dashboards,
    lectures,
    videos,
    assignments,
    chats,
    relevant_content,
    users,
    settings,
    code_exercises,
    gemini_chat
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(subjects.router, prefix="/subjects", tags=["subjects"])
api_router.include_router(weeks.router, prefix="/weeks", tags=["weeks"])
api_router.include_router(lectures.router, prefix="/lectures", tags=["lectures"])
api_router.include_router(relevant_content.router, prefix="/lectures", tags=["lectures"])
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(assignments.router, prefix="/assignments", tags=["assignments"])
api_router.include_router(chats.router, prefix="/chats", tags=["chats"])
api_router.include_router(code_exercises.router, prefix="/code-exercises", tags=["code-exercises"])
api_router.include_router(dashboards.router, prefix="/dashboards", tags=["dashboards"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(settings.router, prefix="/users", tags=["users"])
api_router.include_router(gemini_chat.router, prefix="/chat", tags=["chat"])