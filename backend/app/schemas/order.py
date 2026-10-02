from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class OrderItemBase(BaseModel):
    product_name: str
    brand: Optional[str] = None
    quantity: float
    unit: str
    unit_price: float


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    id: int
    line_total: float
    matched_confidence: Optional[float] = None

    class Config:
        orm_mode = True


class OrderCreate(BaseModel):
    text: str = Field(..., min_length=1)


class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None


class OrderResponse(BaseModel):
    id: str
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    status: str
    items: List[OrderItemResponse] = []
    subtotal: float
    tax: float
    total_amount: float
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ClarificationQuestion(BaseModel):
    question: str
    options: List[str] = []
    question_type: str


class ClarificationResponse(BaseModel):
    questions: List[ClarificationQuestion]