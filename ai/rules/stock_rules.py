from typing import List, Dict
from ai.schemas.ai import ParsedOrderItem, MatchedProduct


class StockRules:
    def check_availability(self, matched_products: List[List[MatchedProduct]], inventory: Dict[str, float]) -> List[Dict]:
        issues = []

        for i, matches in enumerate(matched_products):
            if not matches:
                continue

            best_match = matches[0]
            product_id = best_match.product_id
            available = inventory.get(product_id, 0)

            if available <= 0:
                issues.append({
                    "type": "out_of_stock",
                    "item_index": i,
                    "product_id": product_id,
                    "product_name": best_match.product_name,
                    "available": available,
                    "message": f"'{best_match.product_name}' is out of stock"
                })
            elif available < 5:
                issues.append({
                    "type": "low_stock",
                    "item_index": i,
                    "product_id": product_id,
                    "product_name": best_match.product_name,
                    "available": available,
                    "message": f"Only {available} units of '{best_match.product_name}' left"
                })

        return issues