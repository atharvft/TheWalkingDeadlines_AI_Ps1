#!/usr/bin/env python3
"""Build the application catalog from the raw BigBasket CSV.

The raw file is never edited. The command writes a normalized, deduplicated
catalog that the SQLite seeder can consume. It also works without pandas so a
downloaded Kaggle CSV can be used in a minimal demo environment.
"""

import csv
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional

ROOT = Path(__file__).resolve().parents[1]
RAW_DEFAULT = ROOT / "data" / "raw" / "bigbasket.csv"
OUT_DEFAULT = ROOT / "data" / "catalog" / "normalized_products.json"

PACK_RE = re.compile(r"(?<!\d)(\d+(?:\.\d+)?)\s*(kg|kgs|g|gm|gram|l|lt|ml|pcs?|pack|packet|bottle)\b", re.I)
UNIT_MAP = {"kg": "kg", "kgs": "kg", "g": "g", "gm": "g", "gram": "g", "l": "l", "lt": "l", "ml": "ml", "pc": "pcs", "pcs": "pcs", "pack": "pack", "packet": "pack", "bottle": "bottle"}


def clean(value) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).strip()


def stable_id(source_id: str, name: str, pack_size: str) -> str:
    digest = hashlib.sha1(f"{source_id}|{name}|{pack_size}".encode()).hexdigest()[:16]
    return f"bb-{digest}"


def parse_pack_size(text: str) -> Optional[str]:
    match = PACK_RE.search(text or "")
    if not match:
        return None
    value = float(match.group(1))
    unit = UNIT_MAP[match.group(2).lower()]
    return f"{value:g}{unit}"


def row_to_product(row: Dict[str, str], index: int) -> Optional[dict]:
    name = clean(row.get("product") or row.get("name"))
    if not name:
        return None
    brand = clean(row.get("brand")) or None
    category = clean(row.get("category")) or None
    subcategory = clean(row.get("sub_category") or row.get("subcategory")) or None
    description = clean(row.get("description")) or None
    pack_size = parse_pack_size(" ".join([name, description or ""]))
    price_value = row.get("sale_price") or row.get("market_price") or row.get("price") or "0"
    try:
        price = round(float(str(price_value).replace(",", "")), 2)
    except ValueError:
        price = 0.0
    if price <= 0:
        return None
    source_id = clean(row.get("index") or row.get("id")) or str(index)
    aliases = []
    if brand:
        aliases.append(f"{brand} {name}")
    aliases.append(name)
    pack_unit = re.sub(r"^[\d.]+", "", pack_size or "pcs") or "pcs"
    return {
        "id": stable_id(source_id, name, pack_size or ""),
        "source_product_id": source_id,
        "source_dataset": "bigbasket_entire_product_list_28k",
        "name": name,
        "brand": brand,
        "category": category,
        "subcategory": subcategory,
        "pack_size": pack_size,
        "unit": pack_unit,
        "unit_price": price,
        "description": description,
        "aliases": aliases,
        "is_active": True,
    }


def build_catalog(raw_path: Path = RAW_DEFAULT, output_path: Path = OUT_DEFAULT) -> List[dict]:
    with raw_path.open(newline="", encoding="utf-8-sig") as handle:
        rows = csv.DictReader(handle)
        products: Dict[str, dict] = {}
        for index, row in enumerate(rows):
            product = row_to_product(row, index)
            if product:
                products[product["id"]] = product
    result = sorted(products.values(), key=lambda item: (item.get("category") or "", item["name"], item.get("pack_size") or ""))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    raw = Path(sys.argv[1]) if len(sys.argv) > 1 else RAW_DEFAULT
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else OUT_DEFAULT
    products = build_catalog(raw, output)
    print(f"Built {len(products)} normalized products at {output}")
