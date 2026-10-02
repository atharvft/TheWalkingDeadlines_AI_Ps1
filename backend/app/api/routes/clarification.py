from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter()


class ClarificationQuestion(BaseModel):
    question: str
    options: List[str] = []
    question_type: str


class ClarificationResponse(BaseModel):
    questions: List[ClarificationQuestion]


@router.get("/orders/{order_id}/clarifications", response_model=ClarificationResponse)
async def get_clarifications(order_id: str):
    # TODO: Integrate with clarification_service
    raise HTTPException(status_code=501, detail="Not implemented")