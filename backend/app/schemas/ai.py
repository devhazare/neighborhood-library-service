from typing import List, Optional
from pydantic import BaseModel
from app.schemas.book import BookResponse

class AIEnrichmentResponse(BaseModel):
    summary: Optional[str] = None
    genre: Optional[str] = None
    tags: Optional[List[str]] = None
    reading_level: Optional[str] = None
    recommended_for: Optional[str] = None

class RecommendationItem(BaseModel):
    book: BookResponse
    reason: str

class RecommendationResponse(BaseModel):
    recommendations: List[RecommendationItem]

class ReminderResponse(BaseModel):
    message: str
