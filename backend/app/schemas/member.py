from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict

class MemberBase(BaseModel):
    membership_id: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    status: str = "active"
    joined_date: Optional[date] = None

class MemberCreate(MemberBase):
    pass

class MemberUpdate(BaseModel):
    membership_id: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    joined_date: Optional[date] = None

class MemberResponse(MemberBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class MemberListResponse(BaseModel):
    items: List[MemberResponse]
    total: int
