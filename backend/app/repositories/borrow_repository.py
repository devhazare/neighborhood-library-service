import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from app.models.borrow_transaction import BorrowTransaction
from app.models.book import Book
from app.models.member import Member

def create(db: Session, borrow_data: dict) -> BorrowTransaction:
    txn = BorrowTransaction(**borrow_data)
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn

def get_by_id(db: Session, borrow_id: str) -> Optional[BorrowTransaction]:
    return db.query(BorrowTransaction).filter(BorrowTransaction.id == borrow_id).first()

def get_active_by_member(db: Session, member_id: str) -> List[BorrowTransaction]:
    return db.query(BorrowTransaction).filter(
        and_(BorrowTransaction.member_id == member_id, BorrowTransaction.status.in_(["borrowed", "overdue"]))
    ).all()

def get_active_by_book(db: Session, book_id: str) -> List[BorrowTransaction]:
    return db.query(BorrowTransaction).filter(
        and_(BorrowTransaction.book_id == book_id, BorrowTransaction.status.in_(["borrowed", "overdue"]))
    ).all()

def list_active(db: Session, skip: int = 0, limit: int = 100) -> List[BorrowTransaction]:
    return db.query(BorrowTransaction).filter(
        BorrowTransaction.status.in_(["borrowed", "overdue"])
    ).offset(skip).limit(limit).all()

def count_active(db: Session) -> int:
    return db.query(BorrowTransaction).filter(
        BorrowTransaction.status.in_(["borrowed", "overdue"])
    ).count()

def list_overdue(db: Session, skip: int = 0, limit: int = 100) -> List[BorrowTransaction]:
    return db.query(BorrowTransaction).filter(
        BorrowTransaction.status == "overdue"
    ).offset(skip).limit(limit).all()

def count_overdue(db: Session) -> int:
    return db.query(BorrowTransaction).filter(BorrowTransaction.status == "overdue").count()

def get_by_member(db: Session, member_id: str) -> List[BorrowTransaction]:
    return db.query(BorrowTransaction).filter(BorrowTransaction.member_id == member_id).all()

def update_return(db: Session, borrow_id: str, return_date: datetime.date) -> Optional[BorrowTransaction]:
    txn = get_by_id(db, borrow_id)
    if not txn:
        return None
    txn.return_date = return_date
    txn.status = "returned"
    overdue = (return_date - txn.due_date).days
    txn.overdue_days = max(0, overdue)
    db.commit()
    db.refresh(txn)
    return txn

def mark_overdue_transactions(db: Session, today: datetime.date) -> None:
    """Update all borrowed transactions past their due date to overdue status.

    overdue_days is calculated in Python to remain compatible with both
    SQLite (tests) and PostgreSQL (production).
    """
    overdue_txns = db.query(BorrowTransaction).filter(
        BorrowTransaction.status == "borrowed",
        BorrowTransaction.due_date < today,
    ).all()
    for txn in overdue_txns:
        txn.status = "overdue"
        txn.overdue_days = (today - txn.due_date).days
    db.commit()

def enrich_with_book_member(db: Session, txn: BorrowTransaction) -> dict:
    """Return a dict with book_title and member_name added."""
    book = db.query(Book).filter(Book.id == txn.book_id).first()
    member = db.query(Member).filter(Member.id == txn.member_id).first()
    data = {c.name: getattr(txn, c.name) for c in txn.__table__.columns}
    data["book_title"] = book.title if book else None
    data["member_name"] = member.full_name if member else None
    return data
