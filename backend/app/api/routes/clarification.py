from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_order_service
from app.schemas.order import ClarificationResponse
from app.services.order_service import OrderService

router = APIRouter()


@router.get("/orders/{order_id}/clarifications", response_model=ClarificationResponse)
async def get_clarifications(order_id: str, service: OrderService = Depends(get_order_service)):
    try:
        questions = await service.get_clarifications(order_id)
        return {"questions": questions}
    except Exception as exc:
        if getattr(exc, "code", None) == "ORDER_NOT_FOUND":
            raise HTTPException(status_code=404, detail={"message": str(exc), "code": "ORDER_NOT_FOUND"})
        raise
