import os
import shutil
from pathlib import Path
from fastapi import UploadFile
from app.core.logging import get_logger

logger = get_logger(__name__)

class PDFService:
    def __init__(self, upload_dir: str):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def upload_pdf(self, file: UploadFile, book_id: str) -> str:
        """Save uploaded PDF file and return the file path."""
        filename = f"{book_id}.pdf"
        file_path = self.upload_dir / filename
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        logger.info(f"PDF uploaded for book {book_id} to {file_path}")
        return str(file_path)

    def extract_text(self, file_path: str) -> str:
        """Extract text from first 3 pages of a PDF."""
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            text_parts = []
            for i, page in enumerate(reader.pages):
                if i >= 3:
                    break
                text_parts.append(page.extract_text() or "")
            return "\n".join(text_parts)
        except Exception as e:
            logger.warning(f"PDF text extraction failed for {file_path}: {e}")
            return ""
