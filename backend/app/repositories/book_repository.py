from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional, Tuple
from app.models.book import Book

def create(db: Session, book_data: dict) -> Book:
    book = Book(**book_data)
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

def get_by_id(db: Session, book_id: str) -> Optional[Book]:
    return db.query(Book).filter(Book.id == book_id).first()

def get_by_isbn(db: Session, isbn: str) -> Optional[Book]:
    return db.query(Book).filter(Book.isbn == isbn).first()

def list_all(db: Session, skip: int = 0, limit: int = 100) -> List[Book]:
    return db.query(Book).offset(skip).limit(limit).all()

def count_all(db: Session) -> int:
    return db.query(Book).count()

def search(
    db: Session,
    query: Optional[str] = None,
    category: Optional[str] = None,
    author: Optional[str] = None,
    available_only: bool = False,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[Book], int]:
    """Search books with various filters."""
    q = db.query(Book)

    # Text search across title, author, ISBN
    if query:
        search_term = f"%{query}%"
        q = q.filter(
            or_(
                Book.title.ilike(search_term),
                Book.author.ilike(search_term),
                Book.isbn.ilike(search_term),
                Book.publisher.ilike(search_term),
            )
        )

    # Filter by category
    if category:
        q = q.filter(Book.category.ilike(f"%{category}%"))

    # Filter by author
    if author:
        q = q.filter(Book.author.ilike(f"%{author}%"))

    # Filter by availability
    if available_only:
        q = q.filter(Book.available_copies > 0)

    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return items, total

def update(db: Session, book_id: str, update_data: dict) -> Optional[Book]:
    book = get_by_id(db, book_id)
    if not book:
        return None
    for key, value in update_data.items():
        setattr(book, key, value)
    db.commit()
    db.refresh(book)
    return book

def delete(db: Session, book_id: str) -> bool:
    book = get_by_id(db, book_id)
    if not book:
        return False
    db.delete(book)
    db.commit()
    return True

def update_pdf_path(db: Session, book_id: str, path: str) -> Optional[Book]:
    return update(db, book_id, {"pdf_file_path": path})
