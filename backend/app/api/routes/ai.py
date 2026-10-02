from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.dependencies import get_order_service
from app.core.exceptions import OrderDeskException, http_exception_from_orderdesk
from app.services.ai.errors import AIProviderError
from app.services.order_service import OrderService

router = APIRouter()


class ParseOrderRequest(BaseModel):
    text: str
    provider: Optional[str] = None


class ClarificationRequest(BaseModel):
    context: str
    options: List[str]
    provider: Optional[str] = None


@router.post("/parse-order")
async def parse_order(request: ParseOrderRequest, service: OrderService = Depends(get_order_service)):
    try:
        result = await service.parse_order_with_ai(request.text, provider=request.provider)
        return {"success": True, **result}
    except OrderDeskException as exc:
        raise http_exception_from_orderdesk(exc) from exc
    except AIProviderError as exc:
        raise HTTPException(status_code=503, detail={"message": "AI processing is temporarily unavailable", "code": "AI_UNAVAILABLE"}) from exc


@router.post("/clarification")
async def generate_clarification(request: ClarificationRequest, service: OrderService = Depends(get_order_service)):
    if not request.options:
        raise HTTPException(status_code=400, detail={"message": "At least one catalog option is required", "code": "INVALID_CLARIFICATION"})
    try:
        result = await service.ai_router.generate_clarification(
            request.context, request.options, provider=request.provider
        )
        return {"success": True, "provider": service.ai_router.last_provider, "clarification": result.dict()}
    except AIProviderError as exc:
        raise HTTPException(status_code=503, detail={"message": "AI processing is temporarily unavailable", "code": "AI_UNAVAILABLE"}) from exc
