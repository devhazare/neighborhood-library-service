from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict

class BorrowCreate(BaseModel):
    book_id: str
    member_id: str

class ReturnCreate(BaseModel):
    borrow_id: str

class BorrowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    book_id: str
    member_id: str
    borrow_date: date
    due_date: date
    return_date: Optional[date] = None
    status: str
    overdue_days: int
    reminder_sent: bool
    book_title: Optional[str] = None
    member_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class BorrowListResponse(BaseModel):
    items: List[BorrowResponse]
    total: int
