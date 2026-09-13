"""
Day 12 — Price Monitoring, Trend Delta Calculation & Anomaly Alerting
======================================================================
Learn & Practice historical price tracking & intelligence analytics:
- Comparing current price snapshots against historical baseline data
- Calculating absolute Price Delta (ΔPrice) and Percentage Change (% Change)
- Detecting price drop anomalies, price hikes, and stock status changes
- Generating automated alert notifications for price intelligence monitoring
"""

from datetime import datetime, timezone
import sys
from typing import Any, Dict, List

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def calculate_price_delta(previous_price: float, current_price: float) -> tuple[float, float]:
    """
    Calculates absolute price change and percentage change between snapshots.
    Returns (delta_amount, percentage_change).
    """
    if previous_price <= 0:
        return 0.0, 0.0

    delta_amount = round(current_price - previous_price, 2)
    percent_change = round(((current_price - previous_price) / previous_price) * 100, 2)
    return delta_amount, percent_change


def analyze_price_trends(
    previous_snapshot: List[Dict[str, Any]],
    current_snapshot: List[Dict[str, Any]],
    alert_threshold_pct: float = -10.0,
) -> List[Dict[str, Any]]:
    """
    Compares two price dataset snapshots and identifies price drops, hikes, or stock alerts.
    """
    prev_map = {item["id"]: item for item in previous_snapshot}
    alerts = []

    print(f"[Day 12] Analyzing price trends across {len(current_snapshot)} products...\n")

    for current_item in current_snapshot:
        item_id = current_item["id"]
        title = current_item["name"]
        curr_price = current_item["price"]

        if item_id not in prev_map:
            print(f"✨ NEW PRODUCT DETECTED: {title} @ £{curr_price}")
            continue

        prev_item = prev_map[item_id]
        prev_price = prev_item["price"]

        delta_val, pct_change = calculate_price_delta(prev_price, curr_price)

        # Detect Alert Trigger Conditions
        if pct_change <= alert_threshold_pct:
            alert_type = "PRICE_DROP"
            message = f"🚨 Significant Price Drop! Reduced by {abs(pct_change)}% (-£{abs(delta_val)})"
        elif pct_change > 5.0:
            alert_type = "PRICE_HIKE"
            message = f"📈 Price Increased by +{pct_change}% (+£{delta_val})"
        elif prev_item.get("in_stock", True) and not current_item.get("in_stock", True):
            alert_type = "OUT_OF_STOCK"
            message = "⚠️ Item went Out of Stock!"
        else:
            continue

        alert_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "product_id": item_id,
            "title": title,
            "alert_type": alert_type,
            "previous_price": prev_price,
            "current_price": curr_price,
            "price_delta": delta_val,
            "percent_change": pct_change,
            "message": message,
        }
        alerts.append(alert_record)

    return alerts


def run_day_12_demo():
    # Historical Snapshot (Yesterday)
    historical_data = [
        {"id": "B001", "name": "A Light in the Attic", "price": 51.77, "in_stock": True},
        {"id": "B002", "name": "Tipping the Velvet", "price": 53.74, "in_stock": True},
        {"id": "B003", "name": "Soumission", "price": 50.10, "in_stock": True},
        {"id": "B004", "name": "Sharp Objects", "price": 47.82, "in_stock": True},
    ]

    # Current Snapshot (Today)
    current_data = [
        {"id": "B001", "name": "A Light in the Attic", "price": 42.50, "in_stock": True},   # -17.9% DROP
        {"id": "B002", "name": "Tipping the Velvet", "price": 58.00, "in_stock": True},   # +7.9% HIKE
        {"id": "B003", "name": "Soumission", "price": 50.10, "in_stock": False},         # OUT OF STOCK
        {"id": "B004", "name": "Sharp Objects", "price": 47.82, "in_stock": True},         # UNCHANGED
    ]

    alerts = analyze_price_trends(historical_data, current_data, alert_threshold_pct=-10.0)

    print(f"\n✅ Trend analysis complete. Generated {len(alerts)} Price Intelligence Alerts:\n")
    for alert in alerts:
        print(f"[{alert['alert_type']}] {alert['title']}")
        print(f"   └── {alert['message']}")
        print(f"   └── Details: £{alert['previous_price']} ➔ £{alert['current_price']} (Δ: £{alert['price_delta']})\n")

    return alerts


if __name__ == "__main__":
    run_day_12_demo()
