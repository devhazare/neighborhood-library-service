from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.config import settings
from app.schemas.member import MemberCreate, MemberUpdate, MemberResponse, MemberListResponse
from app.schemas.borrow import BorrowResponse, BorrowListResponse
from app.schemas.ai import RecommendationResponse
from app.services import member_service
from app.services.ai_service import AIService
from app.services.recommendation_service import recommend_books
from app.repositories import borrow_repository

router = APIRouter(prefix="/api/v1/members", tags=["members"])

def get_ai_service():
    return AIService(settings)

@router.post("", response_model=MemberResponse, status_code=201)
def create_member(member_in: MemberCreate, db: Session = Depends(get_db)):
    return member_service.create_member(db, member_in.model_dump())

@router.get("", response_model=MemberListResponse)
def list_members(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    members, total = member_service.list_members(db, skip, limit)
    return MemberListResponse(items=members, total=total)

@router.get("/{member_id}", response_model=MemberResponse)
def get_member(member_id: str, db: Session = Depends(get_db)):
    return member_service.get_member(db, member_id)

@router.put("/{member_id}", response_model=MemberResponse)
def update_member(member_id: str, member_in: MemberUpdate, db: Session = Depends(get_db)):
    data = member_in.model_dump(exclude_none=True)
    return member_service.update_member(db, member_id, data)

@router.get("/{member_id}/borrowed-books", response_model=BorrowListResponse)
def get_borrowed_books(member_id: str, db: Session = Depends(get_db)):
    txns = member_service.get_borrowed_books(db, member_id)
    items = []
    for txn in txns:
        data = borrow_repository.enrich_with_book_member(db, txn)
        items.append(BorrowResponse(**data))
    return BorrowListResponse(items=items, total=len(items))

@router.get("/{member_id}/recommendations", response_model=RecommendationResponse)
def get_recommendations(
    member_id: str,
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service),
):
    recommendations = recommend_books(db, member_id, ai_service)
    return RecommendationResponse(recommendations=recommendations)
