from sqlalchemy.orm import Session
from app.models.member import Member
from app.models.borrow_transaction import BorrowTransaction
from app.repositories import member_repository, borrow_repository
from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import get_logger
from typing import List

logger = get_logger(__name__)

def create_member(db: Session, member_data: dict) -> Member:
    existing = member_repository.get_by_membership_id(db, member_data["membership_id"])
    if existing:
        raise ValidationError(f"Member with membership_id '{member_data['membership_id']}' already exists.")
    return member_repository.create(db, member_data)

def update_member(db: Session, member_id: str, update_data: dict) -> Member:
    member = member_repository.get_by_id(db, member_id)
    if not member:
        raise NotFoundError(f"Member with id '{member_id}' not found.")
    return member_repository.update(db, member_id, update_data)

def get_member(db: Session, member_id: str) -> Member:
    member = member_repository.get_by_id(db, member_id)
    if not member:
        raise NotFoundError(f"Member with id '{member_id}' not found.")
    return member

def list_members(db: Session, skip: int = 0, limit: int = 100):
    members = member_repository.list_all(db, skip, limit)
    total = member_repository.count_all(db)
    return members, total

def get_borrowed_books(db: Session, member_id: str) -> List[BorrowTransaction]:
    get_member(db, member_id)
    return borrow_repository.get_by_member(db, member_id)
