from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class MemberCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None


class Member(MemberCreate):
    id: int
    created_at: datetime


class SpaceCreate(BaseModel):
    name: str
    space_type: str
    capacity: int = Field(gt=0)
    hourly_rate: float = Field(gt=0)
    active: bool = True


class Space(SpaceCreate):
    id: int


class BookingCreate(BaseModel):
    member_id: int
    space_id: int
    start_time: datetime
    end_time: datetime


class Booking(BaseModel):
    id: int
    member_id: int
    space_id: int
    start_time: datetime
    end_time: datetime
    status: str


class InvoiceCreate(BaseModel):
    member_id: int
    booking_id: Optional[int] = None
    amount: float = Field(gt=0)
    due_date: datetime


class Invoice(BaseModel):
    id: int
    member_id: int
    booking_id: Optional[int] = None
    amount: float
    status: str
    issued_at: datetime
    due_date: datetime


class PaymentCreate(BaseModel):
    invoice_id: int
    amount: float = Field(gt=0)
    method: str


class Payment(BaseModel):
    id: int
    invoice_id: int
    amount: float
    paid_at: datetime
    method: str
