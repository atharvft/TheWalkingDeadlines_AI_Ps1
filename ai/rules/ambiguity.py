from typing import List, Dict
from ai.schemas.ai import ParsedOrderItem, MatchedProduct


class AmbiguityDetector:
    def __init__(self, confidence_threshold: float = 0.75):
        self.confidence_threshold = confidence_threshold

    def detect(self, parsed_items: List[ParsedOrderItem], matched_products: List[List[MatchedProduct]]) -> List[Dict]:
        ambiguities = []

        for i, (parsed, matches) in enumerate(zip(parsed_items, matched_products)):
            if not matches:
                ambiguities.append({
                    "type": "no_match",
                    "item_index": i,
                    "expression": parsed.product_expression,
                    "message": f"No products found matching '{parsed.product_expression}'"
                })
                continue

            best_match = matches[0]
            if best_match.confidence < self.confidence_threshold:
                alternatives = [
                    {"product_name": m.product_name, "brand": m.brand, "confidence": m.confidence}
                    for m in matches[:3]
                ]
                ambiguities.append({
                    "type": "low_confidence",
                    "item_index": i,
                    "expression": parsed.product_expression,
                    "best_match": {"product_name": best_match.product_name, "brand": best_match.brand, "confidence": best_match.confidence},
                    "alternatives": alternatives,
                    "message": f"Unclear product: '{parsed.product_expression}'. Did you mean '{best_match.product_name}'?"
                })

            if parsed.brand and best_match.brand and parsed.brand.lower() not in best_match.brand.lower():
                ambiguities.append({
                    "type": "brand_mismatch",
                    "item_index": i,
                    "expression": parsed.product_expression,
                    "requested_brand": parsed.brand,
                    "matched_brand": best_match.brand,
                    "message": f"Requested brand '{parsed.brand}' but matched '{best_match.brand}'"
                })

            if parsed.unit.lower() != best_match.unit.lower():
                ambiguities.append({
                    "type": "unit_mismatch",
                    "item_index": i,
                    "expression": parsed.product_expression,
                    "requested_unit": parsed.unit,
                    "matched_unit": best_match.unit,
                    "message": f"Unit mismatch: requested '{parsed.unit}', product uses '{best_match.unit}'"
                })

        return ambiguities