from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator, Field

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
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(..., min_length=1, max_length=200, description="Book title")
    author: str = Field(..., min_length=1, max_length=100, description="Book author")
    isbn: Optional[str] = Field(None, max_length=20, description="ISBN number")
    total_copies: int = Field(default=1, ge=0, le=1000, description="Total number of copies")
    available_copies: int = Field(default=1, ge=0, description="Available copies")
    published_year: Optional[int] = Field(None, ge=1000, le=2100, description="Publication year")

    @field_validator('title', 'author')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or whitespace only')
        return v.strip()

    @field_validator('isbn')
    @classmethod
    def validate_isbn(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Remove hyphens and spaces for validation
        cleaned = v.replace('-', '').replace(' ', '')
        if not cleaned.isdigit():
            raise ValueError('ISBN must contain only digits, hyphens, and spaces')
        if len(cleaned) not in [10, 13]:
            raise ValueError('ISBN must be 10 or 13 digits long')
        return v

    @field_validator('available_copies')
    @classmethod
    def validate_available_copies(cls, v: int, info) -> int:
        if 'total_copies' in info.data and v > info.data['total_copies']:
            raise ValueError('Available copies cannot exceed total copies')
        return v

class BookUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    isbn: Optional[str] = Field(None, max_length=20)
    publisher: Optional[str] = None
    published_year: Optional[int] = Field(None, ge=1000, le=2100)
    category: Optional[str] = None
    total_copies: Optional[int] = Field(None, ge=0, le=1000)
    available_copies: Optional[int] = Field(None, ge=0)
    shelf_location: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    reading_level: Optional[str] = None
    recommended_for: Optional[str] = None

    @field_validator('title', 'author')
    @classmethod
    def validate_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (not v or not v.strip()):
            raise ValueError('Field cannot be empty or whitespace only')
        return v.strip() if v else v

    @field_validator('isbn')
    @classmethod
    def validate_isbn(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        cleaned = v.replace('-', '').replace(' ', '')
        if not cleaned.isdigit():
            raise ValueError('ISBN must contain only digits, hyphens, and spaces')
        if len(cleaned) not in [10, 13]:
            raise ValueError('ISBN must be 10 or 13 digits long')
        return v

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
