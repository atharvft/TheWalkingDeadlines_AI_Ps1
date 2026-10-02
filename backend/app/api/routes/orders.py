from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()


class OrderItemCreate(BaseModel):
    product_name: str
    brand: Optional[str] = None
    quantity: float
    unit: str
    unit_price: float


class OrderCreate(BaseModel):
    text: str


class OrderResponse(BaseModel):
    id: str
    status: str
    items: List[OrderItemCreate]
    clarification_questions: Optional[List[dict]] = None


class ClarificationAnswer(BaseModel):
    question_index: int
    answer: str


@router.post("/orders", response_model=OrderResponse)
async def create_order(order: OrderCreate):
    # TODO: Integrate with order_service
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/orders/voice", response_model=OrderResponse)
async def create_order_voice(audio: UploadFile = File(...)):
    # TODO: Integrate with ASR + order_service
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str):
    # TODO: Integrate with order_service
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/orders/{order_id}/clarify")
async def answer_clarification(order_id: str, answer: ClarificationAnswer):
    # TODO: Integrate with clarification_service
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/orders/{order_id}/clarify/skip")
async def skip_clarification(order_id: str, answer: ClarificationAnswer):
    # TODO: Integrate with clarification_service
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/orders/{order_id}/confirm")
async def confirm_order(order_id: str):
    # TODO: Integrate with order_service
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/orders/{order_id}/bill")
async def get_bill(order_id: str):
    # TODO: Integrate with billing_service
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/orders/{order_id}/delivery-note")
async def get_delivery_note(order_id: str):
    # TODO: Integrate with billing_service
    raise HTTPException(status_code=501, detail="Not implemented")