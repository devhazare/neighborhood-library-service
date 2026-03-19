from sqlalchemy.orm import Session
from app.models.member import Member
from app.models.borrow_transaction import BorrowTransaction
from app.repositories import member_repository, borrow_repository
from app.core.exceptions import NotFoundError, ValidationError, BusinessRuleError
from app.core.logging import get_logger
from typing import List, Optional, Tuple

logger = get_logger(__name__)

def create_member(db: Session, member_data: dict) -> Member:
    existing = member_repository.get_by_membership_id(db, member_data["membership_id"])
    if existing:
        raise ValidationError(f"Member with membership_id '{member_data['membership_id']}' already exists.")
    if member_data.get("email"):
        email_exists = member_repository.get_by_email(db, member_data["email"])
        if email_exists:
            raise ValidationError(f"Member with email '{member_data['email']}' already exists.")
    return member_repository.create(db, member_data)

def update_member(db: Session, member_id: str, update_data: dict) -> Member:
    member = member_repository.get_by_id(db, member_id)
    if not member:
        raise NotFoundError(f"Member with id '{member_id}' not found.")
    # Check for duplicate membership_id
    if update_data.get("membership_id") and update_data["membership_id"] != member.membership_id:
        existing = member_repository.get_by_membership_id(db, update_data["membership_id"])
        if existing:
            raise ValidationError(f"Member with membership_id '{update_data['membership_id']}' already exists.")
    # Check for duplicate email
    if update_data.get("email") and update_data["email"] != member.email:
        email_exists = member_repository.get_by_email(db, update_data["email"])
        if email_exists:
            raise ValidationError(f"Member with email '{update_data['email']}' already exists.")
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

def search_members(
    db: Session,
    query: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[Member], int]:
    """Search members with various filters."""
    return member_repository.search(
        db,
        query=query,
        status=status,
        skip=skip,
        limit=limit
    )

def delete_member(db: Session, member_id: str) -> bool:
    """Delete a member by ID."""
    member = member_repository.get_by_id(db, member_id)
    if not member:
        raise NotFoundError(f"Member with id '{member_id}' not found.")
    # Check if member has active borrowings
    active_borrowings = borrow_repository.get_active_by_member(db, member_id)
    if active_borrowings:
        raise BusinessRuleError("Cannot delete member with active borrowings. Please return all books first.")
    return member_repository.delete(db, member_id)

def get_borrowed_books(db: Session, member_id: str) -> List[BorrowTransaction]:
    get_member(db, member_id)
    return borrow_repository.get_by_member(db, member_id)

def get_borrowed_books_enriched(db: Session, member_id: str) -> List[dict]:
    """Get borrowed books with book and member info enriched."""
    from app.services import borrow_service
    get_member(db, member_id)
    txns = borrow_repository.get_by_member(db, member_id)
    return borrow_service.enrich_transactions(db, txns)

