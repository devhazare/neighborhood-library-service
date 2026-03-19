import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import List, Optional, Dict
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

def get_active_borrow_by_member_and_book(db: Session, member_id: str, book_id: str) -> Optional[BorrowTransaction]:
    """Check if a member already has an active borrow for a specific book."""
    return db.query(BorrowTransaction).filter(
        and_(
            BorrowTransaction.member_id == member_id,
            BorrowTransaction.book_id == book_id,
            BorrowTransaction.status.in_(["borrowed", "overdue"])
        )
    ).first()

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

def update_return(db: Session, borrow_id: str, return_date: datetime.date, fine_per_day: float = 0.50, max_fine: float = 25.00) -> Optional[BorrowTransaction]:
    txn = get_by_id(db, borrow_id)
    if not txn:
        return None
    txn.return_date = return_date
    txn.status = "returned"
    overdue = (return_date - txn.due_date).days
    txn.overdue_days = max(0, overdue)
    # Calculate fine
    if txn.overdue_days > 0:
        fine = txn.overdue_days * fine_per_day
        txn.fine_amount = min(fine, max_fine)
    db.commit()
    db.refresh(txn)
    return txn

def mark_overdue_transactions(db: Session, today: datetime.date, fine_per_day: float = 0.50, max_fine: float = 25.00) -> None:
    """Update all borrowed transactions past their due date to overdue status.

    overdue_days is calculated in Python to remain compatible with both
    SQLite (tests) and PostgreSQL (production).
    Also calculates accumulated fines.
    """
    overdue_txns = db.query(BorrowTransaction).filter(
        BorrowTransaction.status == "borrowed",
        BorrowTransaction.due_date < today,
    ).all()
    for txn in overdue_txns:
        txn.status = "overdue"
        txn.overdue_days = (today - txn.due_date).days
        # Calculate fine
        fine = txn.overdue_days * fine_per_day
        txn.fine_amount = min(fine, max_fine)
    db.commit()

def pay_fine(db: Session, borrow_id: str, payment_date: datetime.date) -> Optional[BorrowTransaction]:
    """Mark a fine as paid."""
    txn = get_by_id(db, borrow_id)
    if not txn:
        return None
    txn.fine_paid = True
    txn.fine_paid_date = payment_date
    db.commit()
    db.refresh(txn)
    return txn

def get_unpaid_fines(db: Session, member_id: str = None) -> List[BorrowTransaction]:
    """Get all transactions with unpaid fines."""
    query = db.query(BorrowTransaction).filter(
        BorrowTransaction.fine_amount > 0,
        BorrowTransaction.fine_paid == False
    )
    if member_id:
        query = query.filter(BorrowTransaction.member_id == member_id)
    return query.all()

def get_member_fines_summary(db: Session, member_id: str) -> dict:
    """Get fines summary for a member."""
    txns = db.query(BorrowTransaction).filter(
        BorrowTransaction.member_id == member_id,
        BorrowTransaction.fine_amount > 0
    ).all()

    total_fines = sum(float(t.fine_amount) for t in txns)
    paid_fines = sum(float(t.fine_amount) for t in txns if t.fine_paid)
    outstanding_fines = total_fines - paid_fines

    return {
        "total_fines": total_fines,
        "paid_fines": paid_fines,
        "outstanding_fines": outstanding_fines,
        "transactions_with_fines": len(txns)
    }

def enrich_with_book_member(db: Session, txn: BorrowTransaction) -> dict:
    """Return a dict with book_title and member_name added."""
    book = db.query(Book).filter(Book.id == txn.book_id).first()
    member = db.query(Member).filter(Member.id == txn.member_id).first()
    data = {c.name: getattr(txn, c.name) for c in txn.__table__.columns}
    data["book_title"] = book.title if book else None
    data["member_name"] = member.full_name if member else None
    return data

def enrich_transactions_batch(db: Session, transactions: List[BorrowTransaction]) -> List[dict]:
    """Batch enrich transactions with book and member info to avoid N+1 queries."""
    if not transactions:
        return []

    # Collect all unique book_ids and member_ids
    book_ids = {txn.book_id for txn in transactions}
    member_ids = {txn.member_id for txn in transactions}

    # Fetch all books and members in single queries
    books = db.query(Book).filter(Book.id.in_(book_ids)).all()
    members = db.query(Member).filter(Member.id.in_(member_ids)).all()

    # Create lookup dictionaries
    book_map: Dict[str, Book] = {b.id: b for b in books}
    member_map: Dict[str, Member] = {m.id: m for m in members}

    # Enrich transactions
    results = []
    for txn in transactions:
        data = {c.name: getattr(txn, c.name) for c in txn.__table__.columns}
        book = book_map.get(txn.book_id)
        member = member_map.get(txn.member_id)
        data["book_title"] = book.title if book else None
        data["member_name"] = member.full_name if member else None
        results.append(data)

    return results

