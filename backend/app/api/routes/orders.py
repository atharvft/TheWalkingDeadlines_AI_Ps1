from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.core.exceptions import OrderDeskException, http_exception_from_orderdesk
from app.dependencies import get_order_service
from app.schemas.order import OrderCreate
from app.services.order_service import OrderService

router = APIRouter()


class ClarificationAnswer(BaseModel):
    question_index: int
    answer: str


class ClarificationSkip(BaseModel):
    question_index: int


def _handle(exc: OrderDeskException):
    raise http_exception_from_orderdesk(exc)


@router.post("")
async def create_order(order: OrderCreate, service: OrderService = Depends(get_order_service)):
    if not order.text.strip():
        raise HTTPException(status_code=400, detail={"message": "Order text cannot be empty", "code": "INVALID_ORDER"})
    try:
        return await service.create_order_from_text(
            order.text,
            provider=order.provider,
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            customer_address=order.customer_address,
        )
    except OrderDeskException as exc:
        _handle(exc)


@router.post("/voice")
async def create_order_voice(audio: UploadFile = File(...), service: OrderService = Depends(get_order_service)):
    if audio.content_type and not (audio.content_type.startswith("audio/") or audio.content_type in {"video/webm", "video/mp4"}):
        raise HTTPException(status_code=400, detail={"message": "File must be audio", "code": "INVALID_AUDIO"})
    data = await audio.read()
    if not data:
        raise HTTPException(status_code=400, detail={"message": "Audio file is empty", "code": "INVALID_AUDIO"})
    try:
        return await service.create_order_from_voice(
            data, filename=audio.filename or "recording.webm", content_type=audio.content_type
        )
    except OrderDeskException as exc:
        _handle(exc)


@router.post("/parse")
async def parse_order(order: OrderCreate, service: OrderService = Depends(get_order_service)):
    if not order.text.strip():
        raise HTTPException(status_code=400, detail={"message": "Order text cannot be empty", "code": "INVALID_ORDER"})
    try:
        # This is the transaction entry point used by text and voice flows.
        # If an optional language provider is temporarily unavailable, retain
        # the deterministic parser/matcher path instead of rejecting an order.
        return await service.create_order_from_text(order.text, provider=order.provider)
    except OrderDeskException as exc:
        _handle(exc)


@router.get("/{order_id}")
async def get_order(order_id: str, service: OrderService = Depends(get_order_service)):
    result = await service.get_order(order_id)
    if not result:
        raise HTTPException(status_code=404, detail={"message": "Order not found", "code": "ORDER_NOT_FOUND"})
    return result


@router.post("/{order_id}/clarify")
async def answer_clarification(order_id: str, answer: ClarificationAnswer, service: OrderService = Depends(get_order_service)):
    try:
        return await service.answer_clarification(order_id, answer.question_index, answer.answer)
    except OrderDeskException as exc:
        _handle(exc)


@router.post("/{order_id}/clarify/skip")
async def skip_clarification(order_id: str, answer: ClarificationSkip, service: OrderService = Depends(get_order_service)):
    try:
        return await service.skip_clarification(order_id, answer.question_index)
    except OrderDeskException as exc:
        _handle(exc)


@router.post("/{order_id}/confirm")
async def confirm_order(order_id: str, service: OrderService = Depends(get_order_service)):
    try:
        return await service.confirm_order(order_id)
    except OrderDeskException as exc:
        _handle(exc)


@router.get("/{order_id}/bill")
async def get_bill(order_id: str, service: OrderService = Depends(get_order_service)):
    try:
        return await service.get_bill(order_id)
    except OrderDeskException as exc:
        _handle(exc)


@router.get("/{order_id}/delivery-note")
async def get_delivery_note(order_id: str, service: OrderService = Depends(get_order_service)):
    try:
        return await service.get_delivery_note(order_id)
    except OrderDeskException as exc:
        _handle(exc)
