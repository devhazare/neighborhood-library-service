from sqlalchemy.orm import Session
from typing import List, Optional
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

def list_all(db: Session, skip: int = 0, limit: int = 100) -> List[Member]:
    return db.query(Member).offset(skip).limit(limit).all()

def count_all(db: Session) -> int:
    return db.query(Member).count()

def update(db: Session, member_id: str, update_data: dict) -> Optional[Member]:
    member = get_by_id(db, member_id)
    if not member:
        return None
    for key, value in update_data.items():
        setattr(member, key, value)
    db.commit()
    db.refresh(member)
    return member
