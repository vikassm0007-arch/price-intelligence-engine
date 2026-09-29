"""
Day 21 — Enterprise Database ORM & Audit Logs
=============================================
Learn & Practice object-relational mapping (ORM) for price intelligence:
- Mapping Product and PriceHistory entities to relational tables
- Maintaining an audit trail of scraping runs (ScrapeAuditLog)
- Executing analytical joins and trend queries via ORM patterns
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
            # Audit Log Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS scrape_audit_logs (
                    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TEXT,
                    status TEXT,
                    items_scraped INTEGER,
                    errors_count INTEGER
                )
            """)
            # Product Entity Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS product_entities (
                    upc TEXT PRIMARY KEY,
                    title TEXT,
                    category TEXT
                )
            """)
            conn.commit()

    def log_scrape_audit(self, status: str, items_count: int, errors_count: int = 0) -> int:
        now = datetime.now(timezone.utc).isoformat()
        with self.get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO scrape_audit_logs (start_time, status, items_scraped, errors_count) VALUES (?, ?, ?, ?)",
                (now, status, items_count, errors_count),
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

    run_id = orm.log_scrape_audit(status="SUCCESS", items_count=40, errors_count=0)
    print(f"✅ Logged Scrape Audit Run #{run_id} into ORM ledger.")

    logs = orm.get_audit_logs()
    print("\n--- Recent Scrape Audit Run Logs ---")
    for log in logs:
        print(f"  • Run #{log['run_id']} [{log['start_time'][:19]}] Status: {log['status']} | Scraped: {log['items_scraped']} items")


if __name__ == "__main__":
    run_day_21_demo()
