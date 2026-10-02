from typing import List, Dict
from ai.schemas.ai import MatchedProduct, ParsedOrderItem


class ConfidenceCalculator:
    def __init__(self):
        self.weights = {
            "fuzzy": 0.4,
            "semantic": 0.4,
            "unit_match": 0.1,
            "brand_match": 0.1
        }

    def calculate(self, matches: List[Dict], parsed_item: ParsedOrderItem) -> List[MatchedProduct]:
        scored = []
        for match in matches:
            base_score = match.get("score", 0.0)
            match_type = match.get("match_type", "fuzzy")

            unit_match = 1.0 if match.get("unit", "").lower() == parsed_item.unit.lower() else 0.0
            brand_match = 1.0
            if parsed_item.brand and match.get("brand"):
                brand_match = 1.0 if parsed_item.brand.lower() in match["brand"].lower() else 0.0
            elif parsed_item.brand:
                brand_match = 0.0

            final_score = (
                base_score * (self.weights["fuzzy"] if match_type == "fuzzy" else self.weights["semantic"]) +
                unit_match * self.weights["unit_match"] +
                brand_match * self.weights["brand_match"]
            )

            scored.append(MatchedProduct(
                product_id=match["product_id"],
                product_name=match["product_name"],
                brand=match.get("brand"),
                unit=match["unit"],
                unit_price=match["unit_price"],
                confidence=min(final_score, 1.0),
                match_type=match_type
            ))

        return sorted(scored, key=lambda x: x.confidence, reverse=True)