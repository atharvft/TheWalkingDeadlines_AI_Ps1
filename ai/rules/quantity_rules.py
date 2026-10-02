from typing import List, Dict
from ai.schemas.ai import ParsedOrderItem


class QuantityRules:
    MIN_QUANTITY = 0.1
    MAX_QUANTITY = 1000

    def validate(self, parsed_items: List[ParsedOrderItem]) -> List[Dict]:
        issues = []

        for i, item in enumerate(parsed_items):
            if item.quantity < self.MIN_QUANTITY:
                issues.append({
                    "type": "quantity_too_low",
                    "item_index": i,
                    "quantity": item.quantity,
                    "min_allowed": self.MIN_QUANTITY,
                    "message": f"Quantity {item.quantity} is below minimum {self.MIN_QUANTITY}"
                })

            if item.quantity > self.MAX_QUANTITY:
                issues.append({
                    "type": "quantity_too_high",
                    "item_index": i,
                    "quantity": item.quantity,
                    "max_allowed": self.MAX_QUANTITY,
                    "message": f"Quantity {item.quantity} exceeds maximum {self.MAX_QUANTITY}"
                })

            if item.quantity != int(item.quantity) and item.unit in ["pcs", "piece", "dozen"]:
                issues.append({
                    "type": "fractional_quantity",
                    "item_index": i,
                    "quantity": item.quantity,
                    "unit": item.unit,
                    "message": f"Fractional quantity {item.quantity} for unit '{item.unit}' may not be valid"
                })

        return issues