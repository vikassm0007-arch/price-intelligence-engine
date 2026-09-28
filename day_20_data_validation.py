"""
Day 20 — Data Validation & Schema Integrity (Pydantic / Dataclasses)
=====================================================================
Learn & Practice data validation for price intelligence pipelines:
- Defining strongly-typed schemas using dataclasses or Pydantic
- Validating raw scraped values (non-negative price, valid URL format, non-empty titles)
- Filtering corrupted or incomplete data records automatically
"""

from dataclasses import dataclass, field
import sys
from typing import Any, Dict, List
from urllib.parse import urlparse

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


@dataclass
class ValidatedProduct:
    upc: str
    title: str
    price: float
    currency: str = "GBP"
    url: str = ""
    in_stock: bool = True
    errors: List[str] = field(default_factory=list)

    def is_valid(self) -> bool:
        """Validates record fields according to business logic rules."""
        self.errors.clear()

        if not self.upc or len(self.upc.strip()) < 3:
            self.errors.append("Invalid or missing UPC code.")

        if not self.title or len(self.title.strip()) == 0:
            self.errors.append("Product title cannot be empty.")

        if self.price <= 0.0:
            self.errors.append("Price must be greater than 0.")

        if self.url:
            parsed = urlparse(self.url)
            if not parsed.scheme or not parsed.netloc:
                self.errors.append(f"Invalid URL structure: {self.url}")

        return len(self.errors) == 0


def validate_scraped_dataset(raw_dataset: List[Dict[str, Any]]) -> tuple[List[ValidatedProduct], List[ValidatedProduct]]:
    """Validates raw scraped records into valid and rejected records."""
    valid_records = []
    rejected_records = []

    for item in raw_dataset:
        record = ValidatedProduct(
            upc=item.get("upc", ""),
            title=item.get("title", ""),
            price=float(item.get("price", 0.0)),
            currency=item.get("currency", "GBP"),
            url=item.get("url", ""),
            in_stock=bool(item.get("in_stock", True)),
        )

        if record.is_valid():
            valid_records.append(record)
        else:
            rejected_records.append(record)

    return valid_records, rejected_records


def run_day_20_demo():
    print("[Day 20] Running Data Validation & Schema Integrity Pipeline...\n")

    raw_data = [
        {"upc": "BOOK-001", "title": "A Light in the Attic", "price": 51.77, "url": "http://books.toscrape.com/b1"},
        {"upc": "BOOK-002", "title": "Tipping the Velvet", "price": 53.74, "url": "http://books.toscrape.com/b2"},
        {"upc": "", "title": "Corrupted Product", "price": -10.0, "url": "invalid_link"},  # INVALID RECORD
    ]

    valid, rejected = validate_scraped_dataset(raw_data)

    print(f"✅ Valid Records Passed ({len(valid)}):")
    for v in valid:
        print(f"  • [{v.upc}] {v.title} - £{v.price}")

    print(f"\n❌ Rejected Records Filtered ({len(rejected)}):")
    for r in rejected:
        print(f"  • Title: '{r.title}' | Errors: {', '.join(r.errors)}")


if __name__ == "__main__":
    run_day_20_demo()
