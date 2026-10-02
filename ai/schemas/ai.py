from typing import List, Optional

from pydantic import BaseModel, Field


class ParsedOrderItem(BaseModel):
    """A language-layer interpretation; it is not product truth."""

    raw_text: str = ""
    product_expression: str = ""
    product_query: str = ""
    quantity: Optional[float] = 1.0
    unit: Optional[str] = "pcs"
    unit_explicit: bool = False
    quantity_explicit: bool = False
    brand: Optional[str] = None
    pack_size: Optional[str] = None
    pack_size_value: Optional[float] = None
    pack_size_unit: Optional[str] = None
    modifiers: List[str] = Field(default_factory=list)


class ParsedOrder(BaseModel):
    items: List[ParsedOrderItem] = Field(default_factory=list)
    delivery_request: Optional[str] = None
    delivery_address: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    special_instructions: Optional[str] = None
    normalized_text: Optional[str] = None
    delivery_required: bool = False
    delivery_date_text: Optional[str] = None
    delivery_time_text: Optional[str] = None
    delivery_address_text: Optional[str] = None


class MatchedProduct(BaseModel):
    product_id: str
    product_name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    unit: str
    unit_price: float
    pack_size: Optional[str] = None
    confidence: float = 0.0
    match_type: str = "fuzzy"
    reason: List[str] = Field(default_factory=list)
