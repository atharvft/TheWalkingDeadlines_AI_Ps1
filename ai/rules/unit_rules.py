from typing import List, Dict
from ai.schemas.ai import ParsedOrderItem


VALID_UNITS = {
    "weight": ["kg", "g", "gram", "grams"],
    "volume": ["l", "litre", "liter", "litres", "liters", "ml", "millilitre", "milliliter"],
    "count": ["pcs", "piece", "pieces", "dozen"],
    "packaging": ["pack", "packet", "packets", "bottle", "bottles", "box", "boxes"]
}

ALL_VALID_UNITS = [u for units in VALID_UNITS.values() for u in units]

UNIT_CATEGORY = {}
for category, units in VALID_UNITS.items():
    for unit in units:
        UNIT_CATEGORY[unit] = category


class UnitRules:
    def validate(self, parsed_items: List[ParsedOrderItem]) -> List[Dict]:
        issues = []

        for i, item in enumerate(parsed_items):
            normalized_unit = item.unit.lower()
            if normalized_unit not in ALL_VALID_UNITS:
                issues.append({
                    "type": "invalid_unit",
                    "item_index": i,
                    "unit": item.unit,
                    "valid_units": ALL_VALID_UNITS,
                    "message": f"Unknown unit '{item.unit}'. Valid units: {', '.join(ALL_VALID_UNITS)}"
                })

        return issues

    def are_compatible(self, unit1: str, unit2: str) -> bool:
        cat1 = UNIT_CATEGORY.get(unit1.lower())
        cat2 = UNIT_CATEGORY.get(unit2.lower())
        return cat1 == cat2 if cat1 and cat2 else False

    def get_category(self, unit: str) -> str:
        return UNIT_CATEGORY.get(unit.lower(), "unknown")