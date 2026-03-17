from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.exceptions import NotFoundError, ValidationError
from app.core.auth import get_current_active_user
from app.models.user import User
from app.schemas.book import BookCreate, BookUpdate, BookResponse, BookListResponse
from app.schemas.ai import AIEnrichmentResponse, PDFMetadataResponse
from app.services import book_service
from app.services.ai_service import AIService
from app.services.pdf_service import PDFService

router = APIRouter(prefix="/api/v1/books", tags=["books"])

def get_ai_service():
    return AIService(settings)

def get_pdf_service():
    return PDFService(settings.PDF_UPLOAD_DIR)

@router.post("", response_model=BookResponse, status_code=201)
def create_book(
    book_in: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    data = book_in.model_dump(exclude_none=False)
    return book_service.create_book(db, data)

@router.get("", response_model=BookListResponse)
def list_books(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    books, total = book_service.list_books(db, skip, limit)
    return BookListResponse(items=books, total=total)

@router.get("/{book_id}", response_model=BookResponse)
def get_book(
    book_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return book_service.get_book(db, book_id)

@router.put("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: str,
    book_in: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    data = book_in.model_dump(exclude_none=True)
    return book_service.update_book(db, book_id, data)

@router.post("/{book_id}/upload-pdf", response_model=BookResponse)
def upload_pdf(
    book_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    pdf_service: PDFService = Depends(get_pdf_service),
    current_user: User = Depends(get_current_active_user)
):
    return book_service.upload_pdf(db, book_id, file, pdf_service)

@router.post("/{book_id}/ai-enrich", response_model=AIEnrichmentResponse)
def ai_enrich_book(
    book_id: str,
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service),
    pdf_service: PDFService = Depends(get_pdf_service),
    current_user: User = Depends(get_current_active_user)
):
    return book_service.enrich_book_ai(db, book_id, ai_service, pdf_service)


@router.post("/extract-pdf-metadata", response_model=PDFMetadataResponse)
def extract_pdf_metadata(
    file: UploadFile = File(...),
    ai_service: AIService = Depends(get_ai_service),
    pdf_service: PDFService = Depends(get_pdf_service),
    current_user: User = Depends(get_current_active_user)
):
    """Extract book metadata from uploaded PDF using AI."""
    import tempfile
    import os

    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    try:
        # Extract text from PDF
        text = pdf_service.extract_text(tmp_path)
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")

        # Use AI to extract metadata
        metadata = ai_service.extract_pdf_metadata(text)
        return PDFMetadataResponse(**metadata)
    finally:
        # Clean up temp file
        os.unlink(tmp_path)


