"""Catalog-grounded product matching.

The matcher is deliberately index-free and deterministic for the hackathon
demo. Semantic matching remains an optional fallback elsewhere in the tree.
"""

from difflib import SequenceMatcher
from typing import Dict, List

from ai.nlp.normalization import normalize_for_matching
from ai.schemas.ai import MatchedProduct, ParsedOrderItem

try:
    from rapidfuzz.fuzz import ratio
except ImportError:  # pragma: no cover - exercised only in minimal installs
    def ratio(left: str, right: str) -> float:
        return SequenceMatcher(None, left, right).ratio() * 100


class ProductMatcher:
    def __init__(self, catalog_products: List[dict]):
        self.catalog_products = catalog_products

    def match(self, parsed_item: ParsedOrderItem) -> List[MatchedProduct]:
        query = normalize_for_matching(parsed_item.product_query or parsed_item.product_expression)
        requested_brand = normalize_for_matching(parsed_item.brand or "")
        exact: List[MatchedProduct] = []
        alias: List[MatchedProduct] = []
        brand_aware: List[MatchedProduct] = []
        fuzzy: List[MatchedProduct] = []

        for product in self.catalog_products:
            if not product.get("is_active", True):
                continue
            name_key = normalize_for_matching(product.get("name", ""))
            aliases = product.get("aliases") or []
            if isinstance(aliases, str):
                aliases = [aliases]
            alias_keys = {normalize_for_matching(value) for value in aliases}
            brand_key = normalize_for_matching(product.get("brand", ""))
            base_reason = []
            if requested_brand:
                if requested_brand == brand_key or requested_brand in brand_key:
                    base_reason.append(f"Brand matched: {product.get('brand')}")
                else:
                    # Never silently substitute a different requested brand.
                    continue

            if query == name_key:
                exact.append(self._make(product, 0.99, "exact", base_reason + [f"Product matched: {product.get('name')}"]))
                continue
            if query in alias_keys or query == normalize_for_matching(product.get("description", "")):
                alias.append(self._make(product, 0.96, "alias", base_reason + [f"Alias matched: {parsed_item.product_query}"]))
                continue
            combined = f"{name_key} {brand_key} {' '.join(alias_keys)}".strip()
            score = max((ratio(query, value) for value in [name_key, brand_key, *alias_keys, combined] if value), default=0.0) / 100.0 if query else 0.0
            if requested_brand and score >= 0.55:
                brand_aware.append(self._make(product, score, "brand_aware", base_reason + ["Brand-aware catalog match"]))
            elif score >= 0.60:
                fuzzy.append(self._make(product, score, "fuzzy", base_reason + ["Fuzzy catalog match"]))

        # The order of these lists encodes the documented matching policy.
        candidates = exact + alias + sorted(brand_aware + fuzzy, key=lambda item: item.confidence, reverse=True)
        return self._deduplicate(candidates)[:10]

    @staticmethod
    def _make(product: dict, confidence: float, match_type: str, reason: List[str]) -> MatchedProduct:
        return MatchedProduct(
            product_id=str(product["id"]),
            product_name=product["name"],
            brand=product.get("brand"),
            category=product.get("category"),
            unit=product.get("unit", "pcs"),
            unit_price=float(product.get("unit_price", 0)),
            pack_size=product.get("pack_size"),
            confidence=min(max(float(confidence), 0.0), 1.0),
            match_type=match_type,
            reason=reason,
        )

    @staticmethod
    def _deduplicate(candidates: List[MatchedProduct]) -> List[MatchedProduct]:
        seen = set()
        result = []
        for candidate in candidates:
            if candidate.product_id in seen:
                continue
            seen.add(candidate.product_id)
            result.append(candidate)
        return result


def match_products(parsed_items: List[ParsedOrderItem], catalog_products: List[dict]) -> List[List[MatchedProduct]]:
    matcher = ProductMatcher(catalog_products)
    return [matcher.match(item) for item in parsed_items]
