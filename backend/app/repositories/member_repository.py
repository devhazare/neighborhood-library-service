from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional, Tuple
from app.models.member import Member

def create(db: Session, member_data: dict) -> Member:
    member = Member(**member_data)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member

def get_by_id(db: Session, member_id: str) -> Optional[Member]:
    return db.query(Member).filter(Member.id == member_id).first()

def get_by_membership_id(db: Session, membership_id: str) -> Optional[Member]:
    return db.query(Member).filter(Member.membership_id == membership_id).first()

def get_by_email(db: Session, email: str) -> Optional[Member]:
    return db.query(Member).filter(Member.email == email).first()

def list_all(db: Session, skip: int = 0, limit: int = 100) -> List[Member]:
    return db.query(Member).offset(skip).limit(limit).all()

def count_all(db: Session) -> int:
    return db.query(Member).count()

def search(
    db: Session,
    query: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[Member], int]:
    """Search members with various filters."""
    q = db.query(Member)

    # Text search across name, email, membership_id, phone
    if query:
        search_term = f"%{query}%"
        q = q.filter(
            or_(
                Member.full_name.ilike(search_term),
                Member.email.ilike(search_term),
                Member.membership_id.ilike(search_term),
                Member.phone.ilike(search_term),
            )
        )

    # Filter by status
    if status:
        q = q.filter(Member.status == status)

    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return items, total

def update(db: Session, member_id: str, update_data: dict) -> Optional[Member]:
    member = get_by_id(db, member_id)
    if not member:
        return None
    for key, value in update_data.items():
        setattr(member, key, value)
    db.commit()
    db.refresh(member)
    return member

def delete(db: Session, member_id: str) -> bool:
    """Delete a member by ID."""
    member = get_by_id(db, member_id)
    if not member:
        return False
    db.delete(member)
    db.commit()
    return True

