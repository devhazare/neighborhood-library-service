from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.models.book import Book
from app.repositories import book_repository
from app.core.exceptions import NotFoundError, ValidationError
from app.schemas.ai import AIEnrichmentResponse
from app.core.logging import get_logger
from typing import Optional, Tuple, List

logger = get_logger(__name__)

def create_book(db: Session, book_data: dict) -> Book:
    if book_data.get("isbn"):
        existing = book_repository.get_by_isbn(db, book_data["isbn"])
        if existing:
            raise ValidationError(f"A book with ISBN '{book_data['isbn']}' already exists.")
    return book_repository.create(db, book_data)

def update_book(db: Session, book_id: str, update_data: dict) -> Book:
    book = book_repository.get_by_id(db, book_id)
    if not book:
        raise NotFoundError(f"Book with id '{book_id}' not found.")
    if update_data.get("isbn") and update_data["isbn"] != book.isbn:
        existing = book_repository.get_by_isbn(db, update_data["isbn"])
        if existing:
            raise ValidationError(f"A book with ISBN '{update_data['isbn']}' already exists.")
    return book_repository.update(db, book_id, update_data)

def get_book(db: Session, book_id: str) -> Book:
    book = book_repository.get_by_id(db, book_id)
    if not book:
        raise NotFoundError(f"Book with id '{book_id}' not found.")
    return book

def list_books(db: Session, skip: int = 0, limit: int = 100):
    books = book_repository.list_all(db, skip, limit)
    total = book_repository.count_all(db)
    return books, total

def search_books(
    db: Session,
    query: Optional[str] = None,
    category: Optional[str] = None,
    author: Optional[str] = None,
    available_only: bool = False,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[Book], int]:
    """Search books with various filters."""
    return book_repository.search(
        db,
        query=query,
        category=category,
        author=author,
        available_only=available_only,
        skip=skip,
        limit=limit
    )

def delete_book(db: Session, book_id: str) -> bool:
    """Delete a book by ID."""
    book = book_repository.get_by_id(db, book_id)
    if not book:
        raise NotFoundError(f"Book with id '{book_id}' not found.")
    return book_repository.delete(db, book_id)

def upload_pdf(db: Session, book_id: str, file: UploadFile, pdf_service) -> Book:
    book = get_book(db, book_id)
    file_path = pdf_service.upload_pdf(file, book_id)
    return book_repository.update_pdf_path(db, book_id, file_path)

def enrich_book_ai(db: Session, book_id: str, ai_service, pdf_service=None) -> AIEnrichmentResponse:
    book = get_book(db, book_id)
    text = ""
    if book.pdf_file_path and pdf_service:
        text = pdf_service.extract_text(book.pdf_file_path)
    result = ai_service.enrich_book(db, book_id, book.title, book.author, book.category or "", text)
    update_data = {}
    if result.get("summary"):
        update_data["summary"] = result["summary"]
    if result.get("tags"):
        update_data["tags"] = result["tags"]
    if result.get("reading_level"):
        update_data["reading_level"] = result["reading_level"]
    if result.get("recommended_for"):
        update_data["recommended_for"] = result["recommended_for"]
    if update_data:
        book_repository.update(db, book_id, update_data)
    return AIEnrichmentResponse(**result)
