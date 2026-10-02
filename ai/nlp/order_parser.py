from typing import List, Optional
from ai.nlp.normalization import normalize_hinglish_text
from ai.nlp.prompt_templates import ORDER_PARSING_PROMPT
from ai.nlp.response_parser import parse_llm_response
from ai.schemas.ai import ParsedOrder, ParsedOrderItem


class OrderParser:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    async def parse(self, text: str) -> ParsedOrder:
        normalized_text = normalize_hinglish_text(text)
        
        if self.llm_client:
            prompt = ORDER_PARSING_PROMPT.format(text=normalized_text)
            response = await self.llm_client.generate(prompt)
            return parse_llm_response(response)
        
        return self._fallback_parse(normalized_text)

    def _fallback_parse(self, text: str) -> ParsedOrder:
        items = []
        words = text.split()
        
        i = 0
        while i < len(words):
            word = words[i].lower()
            if word.isdigit() or self._is_number_word(word):
                quantity = self._parse_quantity(word, words, i)
                if quantity and i + 1 < len(words):
                    unit = self._extract_unit(words[i + 1])
                    product_expr = self._extract_product_expression(words, i + 2)
                    if product_expr:
                        items.append(ParsedOrderItem(
                            product_expression=product_expr,
                            quantity=quantity,
                            unit=unit
                        ))
            i += 1
        
        return ParsedOrder(items=items)

    def _is_number_word(self, word: str) -> bool:
        number_words = {
            "ek": 1, "do": 2, "teen": 3, "chaar": 4, "paanch": 5,
            "chhah": 6, "saat": 7, "aath": 8, "nau": 9, "das": 10,
            "adha": 0.5, "pauna": 0.75, "sava": 1.25, "dhai": 2.5
        }
        return word in number_words

    def _parse_quantity(self, word: str, words: list, index: int) -> Optional[float]:
        if word.isdigit():
            return float(word)
        
        number_words = {
            "ek": 1, "do": 2, "teen": 3, "chaar": 4, "paanch": 5,
            "chhah": 6, "saat": 7, "aath": 8, "nau": 9, "das": 10,
            "adha": 0.5, "pauna": 0.75, "sava": 1.25, "dhai": 2.5
        }
        
        if word in number_words:
            return number_words[word]
        
        if index + 1 < len(words) and words[index + 1].isdigit():
            return float(words[index + 1])
        
        return None

    def _extract_unit(self, word: str) -> str:
        units = {
            "kg", "kilogram", "kilograms", "kilo",
            "g", "gram", "grams",
            "litre", "liter", "litres", "liters", "l",
            "ml", "millilitre", "milliliter",
            "piece", "pieces", "pcs", "pc",
            "dozen", "dozens",
            "packet", "packets", "pack", "packs",
            "bottle", "bottles",
            "box", "boxes"
        }
        return word if word.lower() in units else "piece"

    def _extract_product_expression(self, words: list, start_idx: int) -> str:
        stop_words = {"aur", "and", "with", "plus", ",", "."}
        product_words = []
        for i in range(start_idx, len(words)):
            if words[i].lower() in stop_words:
                break
            product_words.append(words[i])
        return " ".join(product_words) if product_words else ""