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

    # Read catalog data
    with open(os.path.join(catalog_dir, "products.json")) as f:
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
            unit TEXT NOT NULL,
            unit_price REAL NOT NULL,
            description TEXT,
            aliases TEXT,
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
            INSERT OR REPLACE INTO products (id, name, brand, category, unit, unit_price, description, aliases, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            prod["id"],
            prod["name"],
            prod.get("brand"),
            prod.get("category"),
            prod["unit"],
            prod["unit_price"],
            prod.get("description"),
            json.dumps(prod.get("aliases", [])),
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
    print(f"   Products: {len(products)}")
    print(f"   Categories: {len(categories)}")


if __name__ == "__main__":
    seed_database()