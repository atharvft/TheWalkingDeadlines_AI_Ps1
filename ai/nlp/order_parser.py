"""Deterministic Hinglish order extraction.

This parser produces language hypotheses. Catalog matching and business rules
decide whether those hypotheses are safe to transact.
"""

import re
from typing import List, Optional, Tuple

from ai.nlp.normalization import HINGLISH_NUMBER_MAP, normalize_for_matching, normalize_hinglish_text, normalize_unit
from ai.schemas.ai import ParsedOrder, ParsedOrderItem


DELIVERY_RE = re.compile(r"(?:delivery|deliver|bhej(?:na|do)?|ghar\s+(?:pe|par))\s*(.*)$", re.I)
UNIT_WORDS = {
    "kg", "g", "l", "ml", "pcs", "dozen", "pack", "bottle", "box"
}
KNOWN_BRANDS = {"amul", "aashirvaad", "fortune", "tata", "parle", "india gate", "patanjali"}


class OrderParser:
    def __init__(self, llm_client=None, catalog_terms=None):
        # Kept for compatibility with the scaffold. The deterministic parser is
        # the trusted path even when an optional LLM client is supplied.
        self.llm_client = llm_client
        self.catalog_terms = set(catalog_terms or [])

    async def parse(self, text: str) -> ParsedOrder:
        normalized = normalize_hinglish_text(text)
        items = [self._parse_segment(segment) for segment in self._split_segments(normalized)]
        delivery = self._delivery_details(normalized)
        return ParsedOrder(
            items=[item for item in items if item is not None],
            delivery_request=self._extract_delivery_request(normalized),
            normalized_text=normalized,
            delivery_required=delivery[0],
            delivery_date_text=delivery[1],
            delivery_time_text=delivery[2],
        )

    def _split_segments(self, text: str) -> List[str]:
        text = re.sub(r"\b(?:aur|and|plus)\b", ",", text, flags=re.I)
        return [part.strip(" ,") for part in text.split(",") if part.strip(" ,")]

    def _parse_segment(self, segment: str) -> Optional[ParsedOrderItem]:
        original = segment.strip()
        segment = re.sub(r"\b(?:delivery|deliver|kal|aaj|subah|shaam|tak)\b.*$", "", segment).strip()
        segment = re.sub(r"\b(?:dena|do|chahiye|lena|please|bhaiya|bhai|ji)\b", " ", segment)
        segment = re.sub(r"\s+", " ", segment).strip(" ,.")
        if not segment:
            return None

        quantity, unit, unit_explicit, remainder = self._extract_quantity(segment)
        pack_size = None
        pack_value = None
        pack_unit = None

        # A suffix measure such as "butter 500g" is a pack-size hint, not a
        # request for 500 separate packs.
        if quantity is None:
            suffix = re.search(
                r"\b(\d+(?:\.\d+)?|" + "|".join(map(re.escape, HINGLISH_NUMBER_MAP)) +
                r")\s*(kg|kilo|g|gram|l|litre|liter|ml|piece|pcs|pack|packet|bottle|box)\b",
                segment,
                re.I,
            )
            if suffix and suffix.start() > 0:
                pack_value = self._number(suffix.group(1))
                pack_unit = normalize_unit(suffix.group(2))
                pack_size = f"{pack_value:g}{pack_unit}"
                remainder = (segment[:suffix.start()] + " " + segment[suffix.end():]).strip()
                quantity, unit, unit_explicit = 1.0, "pcs", False

        if quantity is None:
            quantity, unit, unit_explicit, remainder = 1.0, "pcs", False, segment

        remainder = re.sub(r"\b(?:dena|do|chahiye|lena|please)\b", " ", remainder)
        remainder = re.sub(r"\s+", " ", remainder).strip(" ,.")
        if not remainder:
            return None

        brand, product_query = self._extract_brand_and_product(remainder)
        if not product_query:
            return None
        return ParsedOrderItem(
            raw_text=original,
            product_expression=remainder,
            product_query=product_query,
            quantity=quantity,
            unit=unit,
            unit_explicit=unit_explicit,
            brand=brand,
            pack_size=pack_size,
            pack_size_value=pack_value,
            pack_size_unit=pack_unit,
        )

    def _extract_quantity(self, segment: str) -> Tuple[Optional[float], str, bool, str]:
        words = segment.split()
        for index, word in enumerate(words):
            if not self._is_number(word):
                continue
            value = self._number(word)
            if index + 1 < len(words) and normalize_unit(words[index + 1]) in UNIT_WORDS:
                unit = normalize_unit(words[index + 1])
                if unit == "dozen":
                    value *= 12
                    unit = "pcs"
                remainder_words = words[index + 2:]
                if index > 0:
                    remainder_words = words[:index] + remainder_words
                return value, unit, True, " ".join(remainder_words)
            remainder_words = words[index + 1:]
            if index > 0:
                remainder_words = words[:index] + remainder_words
            return value, "pcs", False, " ".join(remainder_words)
        return None, "pcs", False, segment

    def _extract_brand_and_product(self, expression: str) -> Tuple[Optional[str], str]:
        normalized_expression = normalize_for_matching(expression)
        for brand in sorted(KNOWN_BRANDS, key=len, reverse=True):
            normalized_brand = normalize_for_matching(brand)
            if normalized_expression == normalized_brand:
                return brand.title(), ""
            if normalized_expression.startswith(normalized_brand + " "):
                product = normalized_expression[len(normalized_brand):].strip()
                if product in {"g", "-g"}:
                    return None, normalized_expression
                return brand.title(), product
        return None, normalized_expression

    def _extract_delivery_request(self, text: str) -> Optional[str]:
        match = DELIVERY_RE.search(text)
        if match:
            return match.group(1).strip()
        for phrase in ("kal subah", "kal shaam", "tomorrow morning", "aaj"):
            if phrase in text:
                return phrase
        return None

    @staticmethod
    def _delivery_details(text: str) -> Tuple[bool, Optional[str], Optional[str]]:
        lowered = text.lower()
        required = bool(re.search(r"\b(?:delivery|deliver|bhej(?:na|do)?|ghar\s+(?:pe|par))\b", lowered))
        date = next((value for value in ("kal", "aaj", "tomorrow") if re.search(rf"\b{value}\b", lowered)), None)
        time = next((value for value in ("subah", "morning", "shaam", "evening") if re.search(rf"\b{value}\b", lowered)), None)
        return required or bool(date), date, time

    @staticmethod
    def _is_number(word: str) -> bool:
        return bool(re.fullmatch(r"\d+(?:\.\d+)?", word)) or word in HINGLISH_NUMBER_MAP

    @staticmethod
    def _number(word: str) -> float:
        if re.fullmatch(r"\d+(?:\.\d+)?", word):
            return float(word)
        return float(HINGLISH_NUMBER_MAP[word])
