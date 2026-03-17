from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict

class BorrowCreate(BaseModel):
    book_id: str
    member_id: str

class ReturnCreate(BaseModel):
    borrow_id: str

class PayFineRequest(BaseModel):
    borrow_id: str
    amount: Optional[float] = None  # If None, pay full amount

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
    fine_amount: float = 0.0
    fine_paid: bool = False
    fine_paid_date: Optional[date] = None
    book_title: Optional[str] = None
    member_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class BorrowListResponse(BaseModel):
    items: List[BorrowResponse]
    total: int

class FinesSummary(BaseModel):
    member_id: str
    member_name: Optional[str] = None
    total_fines: float
    paid_fines: float
    outstanding_fines: float
    transactions_with_fines: int

