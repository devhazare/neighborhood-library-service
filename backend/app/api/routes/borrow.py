from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.auth import get_current_active_user
from app.models.user import User
from app.schemas.borrow import BorrowCreate, ReturnCreate, BorrowResponse, BorrowListResponse
from app.schemas.ai import ReminderResponse
from app.services import borrow_service
from app.services.ai_service import AIService
from app.repositories import borrow_repository

router = APIRouter(prefix="/api/v1", tags=["borrow"])

def get_ai_service():
    return AIService(settings)

@router.post("/borrow", response_model=BorrowResponse, status_code=201)
def borrow_book(
    borrow_in: BorrowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    txn = borrow_service.borrow_book(db, borrow_in.book_id, borrow_in.member_id)
    data = borrow_repository.enrich_with_book_member(db, txn)
    return BorrowResponse(**data)

@router.post("/return", response_model=BorrowResponse)
def return_book(
    return_in: ReturnCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    txn = borrow_service.return_book(db, return_in.borrow_id)
    data = borrow_repository.enrich_with_book_member(db, txn)
    return BorrowResponse(**data)

@router.get("/borrow/active", response_model=BorrowListResponse)
def list_active(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    txns, total = borrow_service.list_active(db, skip, limit)
    items = [BorrowResponse(**borrow_repository.enrich_with_book_member(db, t)) for t in txns]
    return BorrowListResponse(items=items, total=total)

@router.get("/borrow/overdue", response_model=BorrowListResponse)
def list_overdue(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    txns, total = borrow_service.list_overdue(db, skip, limit)
    items = [BorrowResponse(**borrow_repository.enrich_with_book_member(db, t)) for t in txns]
    return BorrowListResponse(items=items, total=total)

@router.post("/borrow/{borrow_id}/generate-reminder", response_model=ReminderResponse)
def generate_reminder(
    borrow_id: str,
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service),
    current_user: User = Depends(get_current_active_user)
):
    msg = borrow_service.generate_reminder(db, borrow_id, ai_service)
    return ReminderResponse(message=msg)

