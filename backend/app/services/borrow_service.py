import datetime
from sqlalchemy.orm import Session
from app.repositories import borrow_repository, book_repository, member_repository
from app.core.exceptions import NotFoundError, BusinessRuleError
from app.core.config import settings
from app.core.logging import get_logger
from typing import List

logger = get_logger(__name__)

def borrow_book(db: Session, book_id: str, member_id: str):
    book = book_repository.get_by_id(db, book_id)
    if not book:
        raise NotFoundError(f"Book with id '{book_id}' not found.")
    member = member_repository.get_by_id(db, member_id)
    if not member:
        raise NotFoundError(f"Member with id '{member_id}' not found.")
    if member.status != "active":
        raise BusinessRuleError("Member account is not active.")
    if book.available_copies <= 0:
        raise BusinessRuleError("No available copies of this book.")
    active_borrowings = borrow_repository.get_active_by_member(db, member_id)
    if len(active_borrowings) >= settings.MAX_ACTIVE_BORROWINGS:
        raise BusinessRuleError(f"Member has reached the maximum of {settings.MAX_ACTIVE_BORROWINGS} active borrowings.")
    today = datetime.date.today()
    due_date = today + datetime.timedelta(days=settings.MAX_BORROW_DAYS)
    borrow_data = {
        "book_id": book_id,
        "member_id": member_id,
        "borrow_date": today,
        "due_date": due_date,
        "status": "borrowed",
    }
    txn = borrow_repository.create(db, borrow_data)
    book.available_copies -= 1
    db.commit()
    db.refresh(book)
    return txn

def return_book(db: Session, borrow_id: str):
    txn = borrow_repository.get_by_id(db, borrow_id)
    if not txn:
        raise NotFoundError(f"Borrow transaction with id '{borrow_id}' not found.")
    if txn.status == "returned":
        raise BusinessRuleError("This book has already been returned.")
    today = datetime.date.today()
    updated_txn = borrow_repository.update_return(db, borrow_id, today)
    book = book_repository.get_by_id(db, txn.book_id)
    if book:
        book.available_copies += 1
        db.commit()
        db.refresh(book)
    return updated_txn

def list_active(db: Session, skip: int = 0, limit: int = 100):
    txns = borrow_repository.list_active(db, skip, limit)
    total = borrow_repository.count_active(db)
    return txns, total

def list_overdue(db: Session, skip: int = 0, limit: int = 100):
    today = datetime.date.today()
    borrow_repository.mark_overdue_transactions(db, today)
    txns = borrow_repository.list_overdue(db, skip, limit)
    total = borrow_repository.count_overdue(db)
    return txns, total

def generate_reminder(db: Session, borrow_id: str, ai_service) -> str:
    txn = borrow_repository.get_by_id(db, borrow_id)
    if not txn:
        raise NotFoundError(f"Borrow transaction with id '{borrow_id}' not found.")
    from app.repositories import member_repository as mr, book_repository as br
    member = mr.get_by_id(db, txn.member_id)
    book = br.get_by_id(db, txn.book_id)
    today = datetime.date.today()
    overdue_days = max(0, (today - txn.due_date).days) if today > txn.due_date else 0
    msg = ai_service.generate_reminder(
        db, borrow_id,
        member.full_name if member else "Member",
        book.title if book else "the book",
        str(txn.due_date),
        overdue_days,
    )
    txn.reminder_sent = True
    db.commit()
    return msg
