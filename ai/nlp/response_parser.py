import json
import re
from typing import Dict, Any
from ai.schemas.ai import ParsedOrder, ParsedOrderItem


def parse_llm_response(response: str) -> ParsedOrder:
    try:
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
        else:
            data = json.loads(response)
    except json.JSONDecodeError:
        return ParsedOrder(items=[])

    items = []
    for item_data in data.get("items", []):
        items.append(ParsedOrderItem(
            product_expression=item_data.get("product_expression", ""),
            quantity=float(item_data.get("quantity", 1)),
            unit=item_data.get("unit", "piece"),
            brand=item_data.get("brand"),
            modifiers=item_data.get("modifiers", [])
        ))

    return ParsedOrder(
        items=items,
        delivery_address=data.get("delivery_address"),
        customer_name=data.get("customer_name"),
        customer_phone=data.get("customer_phone"),
        special_instructions=data.get("special_instructions")
    )


def parse_clarification_response(response: str) -> list:
    try:
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return json.loads(response)
    except json.JSONDecodeError:
        return []