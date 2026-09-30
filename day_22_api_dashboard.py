"""
Day 22 — FastAPI Price Intelligence Service & Web Dashboard API
================================================================
Learn & Practice building production API services to serve price intelligence data:
- Exposing REST API endpoints for product data, price histories, and price drop alerts
- JSON API serialization and endpoint query parameters
- Serving web dashboard data models
"""

import json
import sys
from typing import Any, Dict, List

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class PriceIntelligenceAPIService:

    def __init__(self):
        self.dataset = [
            {"id": "P-001", "name": "A Light in the Attic", "price": 51.77, "category": "Poetry", "in_stock": True},
            {"id": "P-002", "name": "Tipping the Velvet", "price": 53.74, "category": "Fiction", "in_stock": True},
            {"id": "P-003", "name": "Soumission", "price": 50.10, "category": "Fiction", "in_stock": False},
        ]

    def get_products(self, min_price: float = 0.0) -> List[Dict[str, Any]]:
        """GET /api/v1/products"""
        return [p for p in self.dataset if p["price"] >= min_price]

    def get_price_drops(self, discount_threshold: float = 10.0) -> List[Dict[str, Any]]:
        """GET /api/v1/analytics/price-drops"""
        return [
            {
                "id": "P-001",
                "name": "A Light in the Attic",
                "original_price": 65.00,
                "current_price": 51.77,
                "discount_pct": 20.35,
            }
        ]


def run_day_22_demo():
    print("[Day 22] Initializing FastAPI Price Intelligence API Service...\n")
    api = PriceIntelligenceAPIService()

    products = api.get_products(min_price=50.0)
    print("📡 GET /api/v1/products?min_price=50.0 ➔ Response:")
    print(json.dumps(products, indent=2))

    drops = api.get_price_drops()
    print("\n🚨 GET /api/v1/analytics/price-drops ➔ Response:")
    print(json.dumps(drops, indent=2))


if __name__ == "__main__":
    run_day_22_demo()
