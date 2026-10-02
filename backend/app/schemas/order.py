from pydantic import BaseModel, Field
from typing import Optional, List, Any
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
    text: str
    provider: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None


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
    item_index: Optional[int] = None
    code: Optional[str] = None
    suggestions: List[Any] = []


class ClarificationResponse(BaseModel):
    questions: List[ClarificationQuestion]


class OrderProcessResponse(BaseModel):
    """Envelope consumed by the frontend while keeping the order explicit."""

    order: OrderResponse
    status: str
    clarification_questions: List[ClarificationQuestion] = []
    transcript: Optional[str] = None
    evidence: List[Any] = []
