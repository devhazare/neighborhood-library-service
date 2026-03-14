from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class BookBase(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    published_year: Optional[int] = None
    category: Optional[str] = None
    total_copies: int = 1
    available_copies: int = 1
    shelf_location: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    published_year: Optional[int] = None
    category: Optional[str] = None
    total_copies: Optional[int] = None
    available_copies: Optional[int] = None
    shelf_location: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    reading_level: Optional[str] = None
    recommended_for: Optional[str] = None

class BookResponse(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    summary: Optional[str] = None
    tags: Optional[Any] = None
    reading_level: Optional[str] = None
    recommended_for: Optional[str] = None
    pdf_file_path: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class BookListResponse(BaseModel):
    items: List[BookResponse]
    total: int
