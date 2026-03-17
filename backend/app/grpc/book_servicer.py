"""gRPC Book Service Implementation."""

from sqlalchemy.orm import Session
from app.grpc.generated import books_pb2, books_pb2_grpc, common_pb2
from app.services import book_service
from app.services.ai_service import AIService
from app.services.pdf_service import PDFService
from app.core.database import SessionLocal
from app.core.config import settings
from app.core.exceptions import NotFoundError
import grpc


class BookServicer(books_pb2_grpc.BookServiceServicer):
    """Implementation of the BookService gRPC service."""

    def _get_db(self) -> Session:
        """Get a database session."""
        return SessionLocal()

    def _get_ai_service(self) -> AIService:
        """Get AI service instance."""
        return AIService(settings)

    def _get_pdf_service(self) -> PDFService:
        """Get PDF service instance."""
        return PDFService(settings.PDF_UPLOAD_DIR)

    def _book_to_proto(self, book) -> books_pb2.Book:
        """Convert a book model to protobuf message."""
        return books_pb2.Book(
            id=str(book.id),
            title=book.title,
            author=book.author,
            isbn=book.isbn or "",
            publisher=book.publisher or "",
            published_year=book.published_year or 0,
            category=book.category or "",
            total_copies=book.total_copies,
            available_copies=book.available_copies,
            shelf_location=book.shelf_location or "",
            summary=book.summary or "",
            tags=book.tags or [],
            reading_level=book.reading_level or "",
            recommended_for=book.recommended_for or "",
            pdf_file_path=book.pdf_file_path or "",
            created_at=book.created_at.isoformat() if book.created_at else "",
            updated_at=book.updated_at.isoformat() if book.updated_at else "",
        )

    def CreateBook(self, request: books_pb2.CreateBookRequest, context) -> books_pb2.BookResponse:
        """Create a new book."""
        db = self._get_db()
        try:
            book_data = {
                "title": request.title,
                "author": request.author,
                "isbn": request.isbn if request.isbn else None,
                "publisher": request.publisher if request.publisher else None,
                "published_year": request.published_year if request.published_year else None,
                "category": request.category if request.category else None,
                "total_copies": request.total_copies,
                "available_copies": request.available_copies,
                "shelf_location": request.shelf_location if request.shelf_location else None,
            }
            book = book_service.create_book(db, book_data)
            return books_pb2.BookResponse(book=self._book_to_proto(book))
        finally:
            db.close()

    def GetBook(self, request: common_pb2.IdRequest, context) -> books_pb2.BookResponse:
        """Get a book by ID."""
        db = self._get_db()
        try:
            book = book_service.get_book(db, request.id)
            return books_pb2.BookResponse(book=self._book_to_proto(book))
        except NotFoundError as e:
            context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        finally:
            db.close()

    def ListBooks(self, request: common_pb2.PaginationRequest, context) -> books_pb2.BookListResponse:
        """List all books with pagination."""
        db = self._get_db()
        try:
            books, total = book_service.list_books(db, request.skip, request.limit)
            return books_pb2.BookListResponse(
                items=[self._book_to_proto(b) for b in books],
                total=total,
                skip=request.skip,
                limit=request.limit,
            )
        finally:
            db.close()

    def UpdateBook(self, request: books_pb2.UpdateBookRequest, context) -> books_pb2.BookResponse:
        """Update a book."""
        db = self._get_db()
        try:
            update_data = {}
            if request.HasField("title"):
                update_data["title"] = request.title
            if request.HasField("author"):
                update_data["author"] = request.author
            if request.HasField("isbn"):
                update_data["isbn"] = request.isbn
            if request.HasField("publisher"):
                update_data["publisher"] = request.publisher
            if request.HasField("published_year"):
                update_data["published_year"] = request.published_year
            if request.HasField("category"):
                update_data["category"] = request.category
            if request.HasField("total_copies"):
                update_data["total_copies"] = request.total_copies
            if request.HasField("available_copies"):
                update_data["available_copies"] = request.available_copies
            if request.HasField("shelf_location"):
                update_data["shelf_location"] = request.shelf_location

            book = book_service.update_book(db, request.id, update_data)
            return books_pb2.BookResponse(book=self._book_to_proto(book))
        except NotFoundError as e:
            context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        finally:
            db.close()

    def DeleteBook(self, request: common_pb2.IdRequest, context) -> common_pb2.StatusResponse:
        """Delete a book."""
        db = self._get_db()
        try:
            # Note: Implement delete in book_service if not exists
            book_service.delete_book(db, request.id)
            return common_pb2.StatusResponse(success=True, message="Book deleted successfully")
        except NotFoundError as e:
            context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        finally:
            db.close()

    def SearchBooks(self, request: books_pb2.SearchBooksRequest, context) -> books_pb2.BookListResponse:
        """Search books."""
        db = self._get_db()
        try:
            # Implement search logic
            books, total = book_service.search_books(
                db,
                query=request.query,
                category=request.category if request.HasField("category") else None,
                author=request.author if request.HasField("author") else None,
                skip=request.skip,
                limit=request.limit
            )
            return books_pb2.BookListResponse(
                items=[self._book_to_proto(b) for b in books],
                total=total,
                skip=request.skip,
                limit=request.limit,
            )
        finally:
            db.close()

    def AiEnrichBook(self, request: common_pb2.IdRequest, context) -> books_pb2.AiEnrichmentResponse:
        """Enrich book with AI-generated content."""
        db = self._get_db()
        try:
            ai_service = self._get_ai_service()
            pdf_service = self._get_pdf_service()
            result = book_service.enrich_book_ai(db, request.id, ai_service, pdf_service)
            return books_pb2.AiEnrichmentResponse(
                summary=result.get("summary", ""),
                genre=result.get("genre", ""),
                tags=result.get("tags", []),
                reading_level=result.get("reading_level", ""),
                recommended_for=result.get("recommended_for", ""),
            )
        except NotFoundError as e:
            context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        finally:
            db.close()

    def ExtractPdfMetadata(self, request: books_pb2.ExtractPdfMetadataRequest, context) -> books_pb2.PdfMetadataResponse:
        """Extract metadata from PDF using AI."""
        import tempfile
        import os

        pdf_service = self._get_pdf_service()
        ai_service = self._get_ai_service()

        # Save PDF content to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(request.pdf_content)
            tmp_path = tmp.name

        try:
            text = pdf_service.extract_text(tmp_path)
            if not text.strip():
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Could not extract text from PDF")
                return books_pb2.PdfMetadataResponse()

            metadata = ai_service.extract_pdf_metadata(text)
            return books_pb2.PdfMetadataResponse(
                title=metadata.get("title", ""),
                author=metadata.get("author", ""),
                isbn=metadata.get("isbn", ""),
                publisher=metadata.get("publisher", ""),
                published_year=metadata.get("published_year") or 0,
                category=metadata.get("category", ""),
            )
        finally:
            os.unlink(tmp_path)

