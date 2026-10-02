from typing import List, Dict
from rapidfuzz import fuzz, process


class FuzzyMatcher:
    def __init__(self, threshold: float = 60.0):
        self.threshold = threshold

    def match(self, query: str, catalog: List[Dict]) -> List[Dict]:
        choices = []
        for product in catalog:
            name = f"{product.get('name', '')} {product.get('brand', '')}".strip()
            choices.append((product["id"], name))

        if not choices:
            return []

        ids, names = zip(*choices)
        results = process.extract(query, names, scorer=fuzz.WRatio, limit=10)

        matches = []
        for name, score, idx in results:
            if score >= self.threshold:
                product = catalog[idx]
                matches.append({
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "brand": product.get("brand"),
                    "unit": product["unit"],
                    "unit_price": product["unit_price"],
                    "score": score / 100.0,
                    "match_type": "fuzzy"
                })

        return matches