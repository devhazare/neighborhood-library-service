from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.config import settings
from app.core.exceptions import NotFoundError, ValidationError
from app.schemas.book import BookCreate, BookUpdate, BookResponse, BookListResponse
from app.schemas.ai import AIEnrichmentResponse
from app.services import book_service
from app.services.ai_service import AIService
from app.services.pdf_service import PDFService

router = APIRouter(prefix="/api/v1/books", tags=["books"])

def get_ai_service():
    return AIService(settings)

def get_pdf_service():
    return PDFService(settings.PDF_UPLOAD_DIR)

@router.post("", response_model=BookResponse, status_code=201)
def create_book(book_in: BookCreate, db: Session = Depends(get_db)):
    data = book_in.model_dump(exclude_none=False)
    return book_service.create_book(db, data)

@router.get("", response_model=BookListResponse)
def list_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    books, total = book_service.list_books(db, skip, limit)
    return BookListResponse(items=books, total=total)

@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: str, db: Session = Depends(get_db)):
    return book_service.get_book(db, book_id)

@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: str, book_in: BookUpdate, db: Session = Depends(get_db)):
    data = book_in.model_dump(exclude_none=True)
    return book_service.update_book(db, book_id, data)

@router.post("/{book_id}/upload-pdf", response_model=BookResponse)
def upload_pdf(
    book_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    pdf_service: PDFService = Depends(get_pdf_service),
):
    return book_service.upload_pdf(db, book_id, file, pdf_service)

@router.post("/{book_id}/ai-enrich", response_model=AIEnrichmentResponse)
def ai_enrich_book(
    book_id: str,
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service),
    pdf_service: PDFService = Depends(get_pdf_service),
):
    return book_service.enrich_book_ai(db, book_id, ai_service, pdf_service)
