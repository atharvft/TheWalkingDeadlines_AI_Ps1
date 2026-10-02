#!/usr/bin/env python3
"""Seed database from root data/catalog files."""

import json
import sqlite3
import os
import sys


def seed_database():
    # Paths
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    catalog_dir = os.path.join(root_dir, "data", "catalog")
    db_path = os.path.join(root_dir, "backend", "data", "orderdesk.db")

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Prefer the normalized BigBasket output when it exists. The curated file
    # remains a small offline fallback for demos and tests.
    normalized_path = os.path.join(catalog_dir, "normalized_products.json")
    products_path = normalized_path if os.path.exists(normalized_path) else os.path.join(catalog_dir, "products.json")
    with open(products_path) as f:
        products = json.load(f)

    with open(os.path.join(catalog_dir, "categories.json")) as f:
        categories = json.load(f)

    # Connect to SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            brand TEXT,
            category TEXT,
            subcategory TEXT,
            unit TEXT NOT NULL,
            pack_size TEXT,
            unit_price REAL NOT NULL,
            description TEXT,
            aliases TEXT,
            normalized_name TEXT,
            source_product_id TEXT,
            source_dataset TEXT,
            is_active INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            product_id TEXT PRIMARY KEY,
            stock_quantity REAL DEFAULT 0,
            reserved_quantity REAL DEFAULT 0,
            reorder_level REAL DEFAULT 10,
            last_updated INTEGER,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            display_order INTEGER
        )
    """)

    # Insert categories
    for cat in categories:
        cursor.execute(
            "INSERT OR REPLACE INTO categories (id, name, display_order) VALUES (?, ?, ?)",
            (cat["id"], cat["name"], cat["display_order"])
        )

    # Insert products and inventory
    for prod in products:
        cursor.execute("""
            INSERT OR REPLACE INTO products (id, name, brand, category, subcategory, unit, pack_size, unit_price, description, aliases, normalized_name, source_product_id, source_dataset, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            prod["id"],
            prod["name"],
            prod.get("brand"),
            prod.get("category"),
            prod.get("subcategory"),
            prod["unit"],
            prod.get("pack_size"),
            prod["unit_price"],
            prod.get("description"),
            json.dumps(prod.get("aliases", [])),
            prod.get("normalized_name", prod.get("name", "").lower()),
            prod.get("source_product_id"),
            prod.get("source_dataset", "curated_demo_fallback"),
            1 if prod.get("is_active", True) else 0
        ))

        # Default inventory
        cursor.execute("""
            INSERT OR REPLACE INTO inventory (product_id, stock_quantity, reserved_quantity, reorder_level, last_updated)
            VALUES (?, 100, 0, 10, strftime('%s', 'now'))
        """, (prod["id"],))

    conn.commit()
    conn.close()

    print(f"✅ Database seeded at {db_path}")
    print(f"   Products: {len(products)} ({'normalized BigBasket' if products_path == normalized_path else 'curated fallback'})")
    print(f"   Categories: {len(categories)}")


if __name__ == "__main__":
    seed_database()
