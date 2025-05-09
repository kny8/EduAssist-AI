from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import timedelta
from database.database import get_db
from models import RelevantContent, Lecture, StudySearchResult
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import requests

router = APIRouter()


class RelevantContentRequest(BaseModel):
    lecture_id: int
    user_id: Optional[int] = None  # Optional for personalized content
    content_type: str  # "Video", "PDF", "ExternalLink"
    title: str
    description: Optional[str] = None
    url: HttpUrl


class RelevantContentResponse(RelevantContentRequest):
    id: int
    created_at: str

    class Config:
        from_attributes = True


@router.get("/relevant-content/{lecture_id}", response_model=List[RelevantContentResponse])
def get_relevant_content(lecture_id: int, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(RelevantContent).filter(RelevantContent.lecture_id == lecture_id)

    if user_id:
        query = query.filter(RelevantContent.user_id == user_id)

    content = query.order_by(RelevantContent.created_at).all()

    if not content:
        raise HTTPException(status_code=404, detail="No relevant content found")

    return content


@router.post("/relevant-content/", response_model=RelevantContentResponse)
def add_relevant_content(request: RelevantContentRequest, db: Session = Depends(get_db)):
    new_content = RelevantContent(
        lecture_id=request.lecture_id,
        user_id=request.user_id,
        content_type=request.content_type,
        title=request.title,
        description=request.description,
        url=request.url
    )

    db.add(new_content)
    db.commit()
    db.refresh(new_content)

    return new_content


@router.post("/search-google")
async def search_study_content(data: dict, db: Session = Depends(get_db)):
    """Search for relevant study content using Google Custom Search API with caching."""
    try:
        lecture_id = data.get("lecture_id")
        query = data.get("query", "")

        # Check if we have cached results that are less than 24 hours old
        cached_results = db.query(StudySearchResult).filter(
            and_(
                StudySearchResult.lecture_id == lecture_id,
                StudySearchResult.query == query,
                StudySearchResult.created_at >= func.now() - timedelta(hours=24)
            )
        ).order_by(StudySearchResult.created_at.desc()).limit(5).all()

        if cached_results:
            # Update last_accessed timestamp
            for result in cached_results:
                result.last_accessed = func.now()
            db.commit()

            return {
                "results": [
                    {
                        "title": result.title,
                        "link": result.link,
                        "snippet": result.snippet,
                        "source": result.source
                    }
                    for result in cached_results
                ]
            }

        # Get the lecture to include its content in the search
        lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")

        # Prepare the search query
        if not query:
            name = lecture.name
            if ':' in name:
                name = name.split(':')[1]
            query = f"{name}".strip()

        # Make request to Google Custom Search API
        api_key = "AIzaSyDqbnNUzjNkeuB9ZDK6q3s8eTUCBx0Vz7I"
        search_engine_id = "92d79bedffa8f4270"

        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": search_engine_id,
            "q": query,
            "num": 5
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("items", []):
            result = {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "source": item.get("displayLink", "")
            }
            results.append(result)

            # Cache the result in the database
            db_result = StudySearchResult(
                lecture_id=lecture_id,
                query=query,
                context=lecture.name,
                title=result["title"],
                link=result["link"],
                snippet=result["snippet"],
                source=result["source"]
            )
            db.add(db_result)

        db.commit()
        return {"results": results}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
