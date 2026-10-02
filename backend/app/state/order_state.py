from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from app.schemas.ai import ParsedOrder, MatchedProduct


class OrderStep(str, Enum):
    RECEIVED = "received"
    PARSED = "parsed"
    MATCHED = "matched"
    VALIDATED = "validated"
    CLARIFICATION_NEEDED = "clarification_needed"
    CLARIFICATION_RESOLVED = "clarification_resolved"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"


@dataclass
class OrderState:
    order_id: str
    current_step: OrderStep = OrderStep.RECEIVED
    parsed_order: Optional[ParsedOrder] = None
    matched_products: List[MatchedProduct] = field(default_factory=list)
    clarification_history: List[Dict[str, Any]] = field(default_factory=list)
    awaiting_question_index: Optional[int] = None
    validation_errors: List[str] = field(default_factory=list)
    stock_issues: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "current_step": self.current_step.value,
            "parsed_order": self.parsed_order.dict() if self.parsed_order else None,
            "matched_products": [p.dict() for p in self.matched_products],
            "clarification_history": self.clarification_history,
            "awaiting_question_index": self.awaiting_question_index,
            "validation_errors": self.validation_errors,
            "stock_issues": self.stock_issues
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OrderState":
        state = cls(
            order_id=data["order_id"],
            current_step=OrderStep(data["current_step"]),
            awaiting_question_index=data.get("awaiting_question_index"),
            validation_errors=data.get("validation_errors", []),
            stock_issues=data.get("stock_issues", []),
            clarification_history=data.get("clarification_history", [])
        )
        if data.get("parsed_order"):
            state.parsed_order = ParsedOrder(**data["parsed_order"])
        if data.get("matched_products"):
            state.matched_products = [MatchedProduct(**p) for p in data["matched_products"]]
        return state