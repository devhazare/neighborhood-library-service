from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.config import settings
from app.core.auth import get_current_active_user
from app.models.user import User
from app.schemas.member import MemberCreate, MemberUpdate, MemberResponse, MemberListResponse
from app.schemas.borrow import BorrowResponse, BorrowListResponse
from app.schemas.ai import RecommendationResponse
from app.schemas.common import MessageResponse
from app.services import member_service
from app.services.ai_service import AIService
from app.services.recommendation_service import recommend_books

router = APIRouter(prefix="/api/v1/members", tags=["members"])

def get_ai_service():
    return AIService(settings)

@router.post("", response_model=MemberResponse, status_code=201)
def create_member(
    member_in: MemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return member_service.create_member(db, member_in.model_dump())

@router.get("", response_model=MemberListResponse)
def list_members(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    members, total = member_service.list_members(db, skip, limit)
    return MemberListResponse(items=members, total=total)

@router.get("/search", response_model=MemberListResponse)
def search_members(
    q: Optional[str] = Query(None, description="Search query (name, email, membership ID, phone)"),
    status: Optional[str] = Query(None, description="Filter by status (active/inactive)"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Search and filter members."""
    members, total = member_service.search_members(
        db,
        query=q,
        status=status,
        skip=skip,
        limit=limit
    )
    return MemberListResponse(items=members, total=total)

@router.get("/{member_id}", response_model=MemberResponse)
def get_member(
    member_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return member_service.get_member(db, member_id)

@router.put("/{member_id}", response_model=MemberResponse)
def update_member(
    member_id: str,
    member_in: MemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    data = member_in.model_dump(exclude_none=True)
    return member_service.update_member(db, member_id, data)

@router.delete("/{member_id}", response_model=MessageResponse)
def delete_member(
    member_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a member by ID."""
    member_service.delete_member(db, member_id)
    return MessageResponse(message="Member deleted successfully")

@router.get("/{member_id}/borrowed-books", response_model=BorrowListResponse)
def get_borrowed_books(
    member_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Use service layer with batch enrichment (fixes layer violation)
    enriched = member_service.get_borrowed_books_enriched(db, member_id)
    items = [BorrowResponse(**data) for data in enriched]
    return BorrowListResponse(items=items, total=len(items))

@router.get("/{member_id}/recommendations", response_model=RecommendationResponse)
def get_recommendations(
    member_id: str,
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service),
    current_user: User = Depends(get_current_active_user)
):
    recommendations = recommend_books(db, member_id, ai_service)
    return RecommendationResponse(recommendations=recommendations)

