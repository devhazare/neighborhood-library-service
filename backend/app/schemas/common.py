from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int

class SuccessResponse(BaseModel):
    message: str
    success: bool = True

class MessageResponse(BaseModel):
    """Simple message response for delete operations."""
    message: str

class ErrorResponse(BaseModel):
    detail: str
