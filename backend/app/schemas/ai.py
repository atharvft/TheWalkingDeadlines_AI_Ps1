from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ParsedOrderItem(BaseModel):
    product_expression: str
    quantity: float
    unit: str
    brand: Optional[str] = None
    modifiers: List[str] = []


class ParsedOrder(BaseModel):
    items: List[ParsedOrderItem]
    delivery_address: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    special_instructions: Optional[str] = None


class MatchedProduct(BaseModel):
    product_id: str
    product_name: str
    brand: Optional[str] = None
    unit: str
    unit_price: float
    confidence: float
    match_type: str


class AIProcessingResult(BaseModel):
    parsed_order: ParsedOrder
    matched_products: List[MatchedProduct]
    ambiguities: List[Dict[str, Any]] = []
    stock_issues: List[Dict[str, Any]] = []
    validation_errors: List[str] = []