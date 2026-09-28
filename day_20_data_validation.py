"""
Day 20 — Data Validation & Schema Integrity Engine
===================================================
Learn & Practice advanced data validation for price intelligence pipelines:
- Strongly typed schema validation rules (Price bounds, currency checks, rating validation)
- Automated data sanitization (Whitespace cleaning, price rounding, HTML tag stripping)
- Dead Letter Queue (DLQ) logging for corrupted or missing record fields
"""

from dataclasses import dataclass, field
import json
import re
import sys
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SUPPORTED_CURRENCIES = {"GBP", "USD", "EUR", "INR"}


@dataclass
class ValidatedProductRecord:
    upc: str
    title: str
    price: float
    currency: str = "GBP"
    rating: int = 0
    url: str = ""
    in_stock: bool = True
    errors: List[str] = field(default_factory=list)

    def sanitize(self):
        """Sanitizes raw strings and rounds numeric values."""
        if self.title:
            # Strip remaining HTML tags and extra whitespace
            clean_title = re.sub(r"<[^>]+>", "", self.title)
            self.title = " ".join(clean_title.split())

        self.price = round(self.price, 2)

    def is_valid(self) -> bool:
        """Validates record fields according to production schema rules."""
        self.errors.clear()
        self.sanitize()

        if not self.upc or len(self.upc.strip()) < 3:
            self.errors.append("UPC identifier missing or too short.")

        if not self.title or len(self.title) < 2:
            self.errors.append("Title invalid or too short.")

        if self.price <= 0.0 or self.price > 10000.0:
            self.errors.append(f"Price out of valid bounds: {self.price}")

        if self.currency not in SUPPORTED_CURRENCIES:
            self.errors.append(f"Unsupported currency symbol/code: {self.currency}")

        if self.rating < 0 or self.rating > 5:
            self.errors.append(f"Rating out of bounds (0-5): {self.rating}")

        if self.url:
            parsed = urlparse(self.url)
            if not parsed.scheme or not parsed.netloc:
                self.errors.append(f"Malformed URL format: {self.url}")

        return len(self.errors) == 0


class DataValidationPipeline:

    def __init__(self):
        self.dead_letter_queue: List[Dict[str, Any]] = []

    def process_dataset(self, raw_items: List[Dict[str, Any]]) -> Tuple[List[ValidatedProductRecord], List[Dict[str, Any]]]:
        valid_records = []

        for item in raw_items:
            record = ValidatedProductRecord(
                upc=item.get("upc", ""),
                title=item.get("title", ""),
                price=float(item.get("price", 0.0)),
                currency=item.get("currency", "GBP"),
                rating=int(item.get("rating", 0)),
                url=item.get("url", ""),
                in_stock=bool(item.get("in_stock", True)),
            )

            if record.is_valid():
                valid_records.append(record)
            else:
                dlq_entry = {
                    "raw_data": item,
                    "validation_errors": record.errors,
                }
                self.dead_letter_queue.append(dlq_entry)

        return valid_records, self.dead_letter_queue


def run_day_20_demo():
    print("[Day 20] Running Enhanced Data Validation & Schema Integrity Engine...\n")
    pipeline = DataValidationPipeline()

    raw_data = [
        {"upc": "BOOK-001", "title": "  A Light in the Attic  ", "price": 51.7689, "currency": "GBP", "rating": 3, "url": "http://books.toscrape.com/b1"},
        {"upc": "BOOK-002", "title": "Tipping the Velvet", "price": 53.74, "currency": "GBP", "rating": 5, "url": "http://books.toscrape.com/b2"},
        {"upc": "X", "title": "<b>Corrupted HTML</b>", "price": -50.0, "currency": "XYZ", "rating": 9, "url": "bad_url"},
    ]

    valid_items, dlq = pipeline.process_dataset(raw_data)

    print(f"✅ Validated Records Passed ({len(valid_items)}):")
    for v in valid_items:
        print(f"  • [{v.upc}] {v.title} - {v.currency} {v.price} (Rating: {v.rating}/5)")

    print(f"\n❌ Dead Letter Queue (DLQ) Filtered ({len(dlq)}):")
    for d in dlq:
        print(f"  • Raw Title: '{d['raw_data'].get('title')}'")
        print(f"    └── Validation Errors: {', '.join(d['validation_errors'])}\n")


if __name__ == "__main__":
    run_day_20_demo()
