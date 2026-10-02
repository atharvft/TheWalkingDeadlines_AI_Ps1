"""Provider-neutral schemas for AI output and downstream order processing."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from ai.schemas.ai import MatchedProduct, ParsedOrder, ParsedOrderItem


class AIOrderItem(BaseModel):
    raw_text: str = ""
    product: str
    brand: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    pack_size: Optional[str] = None

    @validator("quantity")
    def quantity_must_be_nonnegative(cls, value):
        if value is not None and value < 0:
            raise ValueError("quantity cannot be negative")
        return value


class DeliveryInfo(BaseModel):
    required: bool = False
    date_text: Optional[str] = None
    time_text: Optional[str] = None
    address_text: Optional[str] = None


class AIParsedOrder(BaseModel):
    items: List[AIOrderItem] = Field(default_factory=list)
    delivery: DeliveryInfo = Field(default_factory=DeliveryInfo)


class ClarificationOutput(BaseModel):
    question: str
    options: List[str] = Field(default_factory=list)


class AIProcessingResult(BaseModel):
    """Compatibility shape retained for callers from the original scaffold."""

    parsed_order: ParsedOrder
    matched_products: List[MatchedProduct]
    ambiguities: List[Dict[str, Any]] = Field(default_factory=list)
    stock_issues: List[Dict[str, Any]] = Field(default_factory=list)
    validation_errors: List[str] = Field(default_factory=list)


def ai_order_json_schema() -> Dict[str, Any]:
    """A strict JSON schema shared by OpenAI structured output and Gemini."""

    nullable_string = {"type": ["string", "null"]}
    nullable_number = {"type": ["number", "null"]}
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["items", "delivery"],
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["raw_text", "product", "brand", "quantity", "unit", "pack_size"],
                    "properties": {
                        "raw_text": {"type": "string"},
                        "product": {"type": "string"},
                        "brand": nullable_string,
                        "quantity": nullable_number,
                        "unit": nullable_string,
                        "pack_size": nullable_string,
                    },
                },
            },
            "delivery": {
                "type": "object",
                "additionalProperties": False,
                "required": ["required", "date_text", "time_text", "address_text"],
                "properties": {
                    "required": {"type": "boolean"},
                    "date_text": nullable_string,
                    "time_text": nullable_string,
                    "address_text": nullable_string,
                },
            },
        },
    }


def clarification_json_schema() -> Dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["question", "options"],
        "properties": {
            "question": {"type": "string"},
            "options": {"type": "array", "items": {"type": "string"}},
        },
    }


__all__ = [
    "AIOrderItem",
    "AIParsedOrder",
    "ClarificationOutput",
    "DeliveryInfo",
    "ParsedOrder",
    "ParsedOrderItem",
    "MatchedProduct",
    "AIProcessingResult",
    "ai_order_json_schema",
    "clarification_json_schema",
]
