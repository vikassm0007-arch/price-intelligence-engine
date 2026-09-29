"""
Day 21 — Enterprise Database ORM & Audit Logs Engine
=====================================================
Learn & Practice object-relational mapping (ORM) for price intelligence:
- Mapping ProductEntity and PriceSnapshotEntity ORM classes to relational tables
- Audit logging of scraping execution runs (ScrapeAuditLog)
- Executing analytical joins and trend queries via ORM repository pattern
"""

from datetime import datetime, timezone
import sqlite3
import sys
from typing import Any, Dict, List

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class PriceIntelligenceORM:

    def __init__(self, db_file: str = "price_intelligence_orm.db"):
        self.db_file = db_file
        self.init_orm_schema()

    def get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    def init_orm_schema(self):
        with self.get_conn() as conn:
            cur = conn.cursor()
            # 1. Audit Log Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS scrape_audit_logs (
                    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TEXT NOT NULL,
                    status TEXT NOT NULL,
                    items_scraped INTEGER NOT NULL,
                    errors_count INTEGER NOT NULL,
                    execution_seconds REAL DEFAULT 0.0
                )
            """)
            # 2. Product Entity Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS product_entities (
                    upc TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    category TEXT
                )
            """)
            # 3. Price History Ledger Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS price_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    upc TEXT NOT NULL,
                    price REAL NOT NULL,
                    currency TEXT NOT NULL,
                    in_stock INTEGER NOT NULL,
                    scraped_at TEXT NOT NULL,
                    FOREIGN KEY (upc) REFERENCES product_entities (upc)
                )
            """)
            conn.commit()

    def save_product_entity(self, upc: str, title: str, category: str, price: float, currency: str = "GBP", in_stock: bool = True):
        now_iso = datetime.now(timezone.utc).isoformat()
        with self.get_conn() as conn:
            cur = conn.cursor()
            # Upsert product entity
            cur.execute(
                """
                INSERT INTO product_entities (upc, title, category)
                VALUES (?, ?, ?)
                ON CONFLICT(upc) DO UPDATE SET title=excluded.title, category=excluded.category
            """,
                (upc, title, category),
            )
            # Insert price snapshot
            cur.execute(
                """
                INSERT INTO price_snapshots (upc, price, currency, in_stock, scraped_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                (upc, price, currency, 1 if in_stock else 0, now_iso),
            )
            conn.commit()

    def log_scrape_audit(self, status: str, items_count: int, errors_count: int = 0, duration: float = 0.0) -> int:
        now_iso = datetime.now(timezone.utc).isoformat()
        with self.get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO scrape_audit_logs (start_time, status, items_scraped, errors_count, execution_seconds)
                VALUES (?, ?, ?, ?, ?)
            """,
                (now_iso, status, items_count, errors_count, duration),
            )
            conn.commit()
            return cur.lastrowid

    def get_audit_logs(self) -> List[Dict[str, Any]]:
        with self.get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM scrape_audit_logs ORDER BY run_id DESC LIMIT 5")
            return [dict(row) for row in cur.fetchall()]


def run_day_21_demo():
    print("[Day 21] Running Enterprise Database ORM & Audit Logging Engine...\n")
    orm = PriceIntelligenceORM("price_intelligence_orm.db")

    orm.save_product_entity(upc="BOOK-101", title="A Light in the Attic", category="Poetry", price=51.77)
    orm.save_product_entity(upc="BOOK-102", title="Tipping the Velvet", category="Fiction", price=53.74)

    run_id = orm.log_scrape_audit(status="SUCCESS", items_count=2, errors_count=0, duration=1.45)
    print(f"✅ Saved product entities and logged Audit Run #{run_id} into ORM ledger.")

    logs = orm.get_audit_logs()
    print("\n--- Recent Scrape Audit Run Logs ---")
    for log in logs:
        print(f"  • Run #{log['run_id']} [{log['start_time'][:19]}] Status: {log['status']} | Items: {log['items_scraped']} | Duration: {log.get('execution_seconds', 0.0)}s")


if __name__ == "__main__":
    run_day_21_demo()
