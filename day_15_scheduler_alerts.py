"""
Day 15 — Scheduled Scraping, Automated Jobs & Webhook Alerts
============================================================
Learn & Practice automated recurring scraping and notification workflows:
- Building automated background scheduling loops
- Tracking price drops across recurring execution cycles
- Dispatching simulated Webhook / Discord / Slack notifications on price anomaly triggers
"""

from datetime import datetime, timezone
import json
import re
import sys
import time
from typing import Any, Dict, List
import requests
from bs4 import BeautifulSoup

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def simulate_webhook_dispatch(alert_payload: Dict[str, Any]):
    """Simulates sending an alert payload to a Slack/Discord/Custom Webhook endpoint."""
    print(f"🔔 [WEBHOOK DISPATCH] ➔ Event: {alert_payload['event']}")
    print(f"   └── Product: {alert_payload['title']} (UPC: {alert_payload['upc']})")
    print(f"   └── Price Drop: £{alert_payload['previous_price']} ➔ £{alert_payload['current_price']} ({alert_payload['discount_pct']}% OFF)")
    print(f"   └── Timestamp: {alert_payload['timestamp']}\n")


class ScheduledPriceMonitor:

    def __init__(self, target_url: str = "http://books.toscrape.com/", alert_threshold_pct: float = 10.0):
        self.target_url = target_url
        self.alert_threshold_pct = alert_threshold_pct
        self.price_history_cache: Dict[str, float] = {}

    def run_check_cycle(self) -> int:
        print(f"\n⏰ [{datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}] Running Scheduled Price Monitoring Cycle...")
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.get(self.target_url, headers=headers, timeout=10)
            response.raise_for_status()
            response.encoding = "utf-8"
        except Exception as err:
            print(f"❌ Failed to fetch monitoring page: {err}")
            return 0

        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select("article.product_pod")
        alerts_triggered = 0

        for idx, card in enumerate(cards[:5], start=1):
            title_el = card.select_one("h3 > a")
            price_el = card.select_one(".price_color")

            upc = f"BOOK-{idx:03d}"
            title = title_el.get("title") or title_el.get_text(strip=True) if title_el else "Unknown"
            price_str = price_el.get_text(strip=True) if price_el else "0.0"

            match = re.search(r"[\d,]+\.\d+|\d+", price_str.replace(",", ""))
            curr_price = float(match.group(0)) if match else 0.0

            # Compare against cached historical price
            if upc in self.price_history_cache:
                prev_price = self.price_history_cache[upc]
                if prev_price > 0:
                    discount_pct = round(((prev_price - curr_price) / prev_price) * 100, 2)
                    if discount_pct >= self.alert_threshold_pct:
                        alerts_triggered += 1
                        payload = {
                            "event": "PRICE_DROP_ALERT",
                            "upc": upc,
                            "title": title,
                            "previous_price": prev_price,
                            "current_price": curr_price,
                            "discount_pct": discount_pct,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                        simulate_webhook_dispatch(payload)

            # Update cache with current price snapshot
            self.price_history_cache[upc] = curr_price

        print(f"✅ Cycle complete. Updated {len(cards[:5])} price records in cache.")
        return alerts_triggered


def run_day_15_demo():
    print("[Day 15] Demonstrating Scheduled Scraping & Webhook Alert Engine...\n")
    monitor = ScheduledPriceMonitor(alert_threshold_pct=10.0)

    # Cycle 1: Baseline cache population
    print("--- Cycle 1: Populating Baseline Price Cache ---")
    monitor.run_check_cycle()

    # Simulate a price drop in cache for Cycle 2 (Previous price £65.00 vs Current price £51.77 -> 20.35% drop)
    print("\n📉 Simulating historical price drop in cache for BOOK-001 (£65.00 ➔ £51.77)...")
    monitor.price_history_cache["BOOK-001"] = 65.00

    # Cycle 2: Triggering automated webhook alert
    print("\n--- Cycle 2: Executing Automated Check Cycle ---")
    alerts = monitor.run_check_cycle()
    print(f"Total alerts dispatched to webhook: {alerts}\n")


if __name__ == "__main__":
    run_day_15_demo()
