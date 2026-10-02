from typing import List, Optional
from ai.matching.fuzzy_matcher import FuzzyMatcher
from ai.matching.semantic_matcher import SemanticMatcher
from ai.matching.confidence import ConfidenceCalculator
from ai.schemas.ai import ParsedOrderItem, MatchedProduct


class ProductMatcher:
    def __init__(self, catalog_products: List[dict]):
        self.catalog_products = catalog_products
        self.fuzzy_matcher = FuzzyMatcher()
        self.semantic_matcher = SemanticMatcher()
        self.confidence_calculator = ConfidenceCalculator()

    def match(self, parsed_item: ParsedOrderItem) -> List[MatchedProduct]:
        fuzzy_matches = self.fuzzy_matcher.match(parsed_item.product_expression, self.catalog_products)
        semantic_matches = self.semantic_matcher.match(parsed_item.product_expression, self.catalog_products)

        combined = self._combine_matches(fuzzy_matches, semantic_matches)
        scored = self.confidence_calculator.calculate(combined, parsed_item)

        return scored[:5]

    def _combine_matches(self, fuzzy: List, semantic: List) -> List:
        seen = {}
        for match in fuzzy + semantic:
            pid = match["product_id"]
            if pid not in seen or match["score"] > seen[pid]["score"]:
                seen[pid] = match
        return list(seen.values())


def match_products(parsed_items: List[ParsedOrderItem], catalog_products: List[dict]) -> List[List[MatchedProduct]]:
    matcher = ProductMatcher(catalog_products)
    return [matcher.match(item) for item in parsed_items]