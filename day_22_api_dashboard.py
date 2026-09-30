"""
Day 22 — FastAPI Price Intelligence Service & Web Dashboard API
================================================================
Learn & Practice building production REST API services to serve price intelligence data:
- Exposing REST API endpoints for product data, price histories, and price drop alerts
- Query filtering (category, price bounds, availability) & JSON API serialization
- Serving real-time analytics data models for web dashboard visualization
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
            {"id": "P-001", "name": "A Light in the Attic", "price": 51.77, "category": "Poetry", "in_stock": True, "discount_pct": 20.35},
            {"id": "P-002", "name": "Tipping the Velvet", "price": 53.74, "category": "Fiction", "in_stock": True, "discount_pct": 0.0},
            {"id": "P-003", "name": "Soumission", "price": 50.10, "category": "Fiction", "in_stock": False, "discount_pct": 0.0},
            {"id": "P-004", "name": "Sharp Objects", "price": 47.82, "category": "Mystery", "in_stock": True, "discount_pct": 15.20},
        ]

    def get_products(self, min_price: float = 0.0, category: str | None = None) -> List[Dict[str, Any]]:
        """GET /api/v1/products"""
        results = [p for p in self.dataset if p["price"] >= min_price]
        if category:
            results = [p for p in results if p["category"].lower() == category.lower()]
        return results

    def get_price_drops(self, min_discount_pct: float = 10.0) -> List[Dict[str, Any]]:
        """GET /api/v1/analytics/price-drops"""
        return [p for p in self.dataset if p.get("discount_pct", 0.0) >= min_discount_pct]

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """GET /api/v1/analytics/summary"""
        total = len(self.dataset)
        prices = [p["price"] for p in self.dataset]
        in_stock_count = sum(1 for p in self.dataset if p["in_stock"])
        alert_count = sum(1 for p in self.dataset if p.get("discount_pct", 0.0) >= 10.0)

        return {
            "total_products_monitored": total,
            "average_price": round(sum(prices) / total, 2) if total else 0.0,
            "stock_rate_pct": round((in_stock_count / total) * 100, 1) if total else 0.0,
            "active_price_drop_alerts": alert_count,
        }


def run_day_22_demo():
    print("[Day 22] Initializing Production FastAPI Price Intelligence API Service...\n")
    api = PriceIntelligenceAPIService()

    summary = api.get_dashboard_summary()
    print("📊 GET /api/v1/analytics/summary ➔ Dashboard Response:")
    print(json.dumps(summary, indent=2))

    products = api.get_products(category="Fiction")
    print("\n📡 GET /api/v1/products?category=Fiction ➔ Response:")
    print(json.dumps(products, indent=2))

    drops = api.get_price_drops(min_discount_pct=10.0)
    print("\n🚨 GET /api/v1/analytics/price-drops?min_discount_pct=10.0 ➔ Response:")
    print(json.dumps(drops, indent=2))


if __name__ == "__main__":
    run_day_22_demo()
