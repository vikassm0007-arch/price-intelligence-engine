"""
Day 14 — SQLite Database Persistence & Historical Ledger
=========================================================
Learn & Practice database persistence for Price Intelligence:
- Designing relational SQLite schema (products & price_history tables)
- Upserting product catalog records
- Appending timestamped historical price snapshots
- Querying price trends, minimum prices, and historical ledgers using SQL
"""

from datetime import datetime, timezone
import sqlite3
import sys
from typing import Any, Dict, List

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class PriceDatabase:

    def __init__(self, db_path: str = "price_intelligence.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initializes relational tables for products and timestamped price snapshots."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Products Master Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    product_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    category TEXT,
                    url TEXT,
                    created_at TEXT NOT NULL
                )
            """)

            # 2. Price History Ledger Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT NOT NULL,
                    price REAL NOT NULL,
                    currency TEXT NOT NULL,
                    stock_quantity INTEGER NOT NULL,
                    scraped_at TEXT NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES products (product_id)
                )
            """)
            conn.commit()

    def save_product_snapshot(self, product: Dict[str, Any]):
        """Saves or updates product master info and appends a price history snapshot."""
        now_iso = datetime.now(timezone.utc).isoformat()
        prod_id = product["upc"]

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Upsert into products master
            cursor.execute(
                """
                INSERT INTO products (product_id, title, category, url, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(product_id) DO UPDATE SET
                    title=excluded.title,
                    category=excluded.category,
                    url=excluded.url
            """,
                (prod_id, product["title"], product.get("category", "General"), product.get("url", ""), now_iso),
            )

            # Insert into price history ledger
            cursor.execute(
                """
                INSERT INTO price_history (product_id, price, currency, stock_quantity, scraped_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    prod_id,
                    product["price"],
                    product.get("currency", "GBP"),
                    product.get("stock_quantity", 1),
                    now_iso,
                ),
            )
            conn.commit()

    def get_price_ledger(self, product_id: str) -> List[Dict[str, Any]]:
        """Queries historical price ledger for a specific product."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT p.title, ph.price, ph.currency, ph.stock_quantity, ph.scraped_at
                FROM price_history ph
                JOIN products p ON ph.product_id = p.product_id
                WHERE ph.product_id = ?
                ORDER BY ph.scraped_at ASC
            """,
                (product_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def query_lowest_prices(self, limit: int = 5) -> List[Dict[str, Any]]:
        """SQL Query returning products sorted by lowest recent price."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT p.product_id, p.title, p.category, ph.price, ph.currency, ph.scraped_at
                FROM products p
                JOIN price_history ph ON p.product_id = ph.product_id
                GROUP BY p.product_id
                HAVING ph.scraped_at = MAX(ph.scraped_at)
                ORDER BY ph.price ASC
                LIMIT ?
            """,
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]


def run_day_14_demo():
    print("[Day 14] Running SQLite Persistence & Historical Ledger Pipeline...\n")
    db = PriceDatabase("price_intelligence.db")

    # Sample Scraped Products across multiple days
    sample_products = [
        {"upc": "UPC-001", "title": "A Light in the Attic", "price": 51.77, "category": "Poetry"},
        {"upc": "UPC-002", "title": "Tipping the Velvet", "price": 53.74, "category": "Fiction"},
        {"upc": "UPC-003", "title": "Soumission", "price": 50.10, "category": "Fiction"},
    ]

    print("💾 Persisting initial scraped snapshot into SQLite database...")
    for prod in sample_products:
        db.save_product_snapshot(prod)

    # Simulate price drop for UPC-001 on next crawl
    print("📉 Simulating price drop update for UPC-001 (£51.77 ➔ £42.50)...")
    discounted_prod = {"upc": "UPC-001", "title": "A Light in the Attic", "price": 42.50, "category": "Poetry"}
    db.save_product_snapshot(discounted_prod)

    # Query Historical Ledger
    print("\n--- Price History Ledger for UPC-001 ---")
    ledger = db.get_price_ledger("UPC-001")
    for row in ledger:
        print(f"  • [{row['scraped_at'][:19]}] {row['title']} ➔ {row['currency']} {row['price']}")

    # Query Top Lowest Prices
    print("\n--- SQL Query: Lowest Priced Items ---")
    lowest = db.query_lowest_prices(limit=3)
    for row in lowest:
        print(f"  • [{row['category']}] {row['title']} - {row['currency']} {row['price']}")


if __name__ == "__main__":
    run_day_14_demo()
