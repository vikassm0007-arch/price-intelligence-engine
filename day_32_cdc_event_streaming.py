"""
Day 32 — Change Data Capture (CDC), Event Streaming & PubSub Dispatch Bus
=========================================================================
Learn & Practice enterprise event-driven architectures for price intelligence:
- Change Data Capture (CDC): Detecting granular state transitions across scrape runs
    • NEW_PRODUCT_DISCOVERED
    • PRICE_DROP / PRICE_HIKE (with percentage delta)
    • OUT_OF_STOCK / BACK_IN_STOCK
    • PRODUCT_DELISTED
- Pub/Sub Event Bus: Decoupling consumers from scraping engines
- Event Handlers:
    • Real-Time Webhook Alert Dispatcher
    • Cold Audit Log Appender
    • Real-Time Market Volatility Metrics Calculator
"""

from datetime import datetime, timezone
import json
import re
import sys
import time
from typing import Any, Callable, Dict, List, Optional
import requests
from bs4 import BeautifulSoup

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class PriceChangeEvent:
    """Represents a discrete Change Data Capture (CDC) event."""

    def __init__(
        self,
        event_type: str,
        upc: str,
        title: str,
        old_val: Any = None,
        new_val: Any = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.event_id = f"EVT-{int(time.time()*1000)}-{upc}"
        self.event_type = event_type
        self.upc = upc
        self.title = title
        self.old_val = old_val
        self.new_val = new_val
        self.metadata = metadata or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "upc": self.upc,
            "title": self.title,
            "old_value": self.old_val,
            "new_value": self.new_val,
            "metadata": self.metadata,
        }


class EventStreamingBus:
    """Pub/Sub broker routing CDC events to registered listener subscribers."""

    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[PriceChangeEvent], None]]] = {}

    def subscribe(self, event_type: str, handler: Callable[[PriceChangeEvent], None]):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    def publish(self, event: PriceChangeEvent):
        # Notify specific event listeners
        if event.event_type in self.subscribers:
            for handler in self.subscribers[event.event_type]:
                handler(event)
        # Notify wildcard listeners
        if "*" in self.subscribers:
            for handler in self.subscribers["*"]:
                handler(event)


class ChangeDataCaptureEngine:
    """Computes differential state transitions between consecutive catalog snapshots."""

    def __init__(self, event_bus: EventStreamingBus):
        self.bus = event_bus
        self.previous_snapshot: Dict[str, Dict[str, Any]] = {}

    def ingest_snapshot(self, current_products: List[Dict[str, Any]]) -> int:
        current_map = {p["upc"]: p for p in current_products}
        events_emitted = 0

        # 1. Detect New Products & Attribute Updates
        for upc, curr in current_map.items():
            if upc not in self.previous_snapshot:
                evt = PriceChangeEvent(
                    event_type="NEW_PRODUCT_DISCOVERED",
                    upc=upc,
                    title=curr["title"],
                    new_val=curr["price"],
                )
                self.bus.publish(evt)
                events_emitted += 1
            else:
                prev = self.previous_snapshot[upc]

                # Price Change Check
                if curr["price"] != prev["price"]:
                    delta_pct = round(((curr["price"] - prev["price"]) / prev["price"]) * 100, 2)
                    etype = "PRICE_DROP" if curr["price"] < prev["price"] else "PRICE_HIKE"
                    evt = PriceChangeEvent(
                        event_type=etype,
                        upc=upc,
                        title=curr["title"],
                        old_val=prev["price"],
                        new_val=curr["price"],
                        metadata={"delta_percent": delta_pct},
                    )
                    self.bus.publish(evt)
                    events_emitted += 1

                # Stock Availability Change Check
                if curr["in_stock"] != prev["in_stock"]:
                    etype = "OUT_OF_STOCK" if not curr["in_stock"] else "BACK_IN_STOCK"
                    evt = PriceChangeEvent(
                        event_type=etype,
                        upc=upc,
                        title=curr["title"],
                        old_val=prev["in_stock"],
                        new_val=curr["in_stock"],
                    )
                    self.bus.publish(evt)
                    events_emitted += 1

        # 2. Detect Delisted Products
        for upc, prev in self.previous_snapshot.items():
            if upc not in current_map:
                evt = PriceChangeEvent(
                    event_type="PRODUCT_DELISTED",
                    upc=upc,
                    title=prev["title"],
                    old_val=prev["price"],
                )
                self.bus.publish(evt)
                events_emitted += 1

        # Update snapshot state
        self.previous_snapshot = current_map
        return events_emitted


def live_scrape_sample(url: str = "http://books.toscrape.com/") -> List[Dict[str, Any]]:
    """Fetches and parses a catalog sample."""
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.select("article.product_pod")
    products = []

    for idx, card in enumerate(cards[:5], start=1):
        title_el = card.select_one("h3 > a")
        price_el = card.select_one(".price_color")

        title = title_el.get("title") or title_el.get_text(strip=True) if title_el else "Unknown"
        price_str = price_el.get_text(strip=True) if price_el else "0.0"

        match = re.search(r"[\d,]+\.\d+|\d+", price_str.replace(",", ""))
        price_val = float(match.group(0)) if match else 0.0

        products.append({
            "upc": f"BOOK-{idx:03d}",
            "title": title,
            "price": price_val,
            "in_stock": True,
        })
    return products


def run_day_32_demo():
    print("================================================================================")
    print("  Day 32 — Change Data Capture (CDC), Event Streaming & PubSub Dispatch Bus")
    print("================================================================================\n")

    event_bus = EventStreamingBus()
    event_log: List[Dict[str, Any]] = []

    # Subscriber 1: Real-time Alert Notifier
    def alert_listener(evt: PriceChangeEvent):
        if evt.event_type == "PRICE_DROP":
            pct = evt.metadata.get("delta_percent", 0.0)
            print(f"🚨 [ALERT WEBHOOK] {evt.title} price dropped: £{evt.old_val} ➔ £{evt.new_val} ({pct}%)")

    # Subscriber 2: Audit Logger
    def audit_logger(evt: PriceChangeEvent):
        event_log.append(evt.to_dict())

    # Register listeners
    event_bus.subscribe("PRICE_DROP", alert_listener)
    event_bus.subscribe("*", audit_logger)

    cdc_engine = ChangeDataCaptureEngine(event_bus)

    # Cycle 1: Baseline Ingestion
    print("--- Cycle 1: Baseline Ingestion (Discovering Catalog) ---")
    initial_products = live_scrape_sample()
    events_c1 = cdc_engine.ingest_snapshot(initial_products)
    print(f"✅ Ingested {len(initial_products)} products. Emitted {events_c1} CDC events.\n")

    # Cycle 2: Market Event Simulation (Price drop on item 1, out of stock on item 2, new item 6)
    print("--- Cycle 2: Market Change Simulation (Price Drop, Stock Change, New Arrival) ---")
    updated_products = [
        {"upc": "BOOK-001", "title": initial_products[0]["title"], "price": 42.50, "in_stock": True},  # Price drop!
        {"upc": "BOOK-002", "title": initial_products[1]["title"], "price": 53.74, "in_stock": False}, # Out of stock!
        {"upc": "BOOK-003", "title": initial_products[2]["title"], "price": 50.10, "in_stock": True},
        {"upc": "BOOK-004", "title": initial_products[3]["title"], "price": 47.82, "in_stock": True},
        {"upc": "BOOK-006", "title": "New Release Best Seller", "price": 38.99, "in_stock": True},     # New product!
    ]

    events_c2 = cdc_engine.ingest_snapshot(updated_products)
    print(f"✅ Processed modified cycle. Emitted {events_c2} new CDC events.\n")

    print(f"📊 Total Streamed Events Collected in Bus: {len(event_log)}")
    for e in event_log[-4:]:
        print(f"  • [{e['event_type']}] {e['title']} (Old: {e['old_value']} | New: {e['new_value']})")

    print("\n✅ Day 32 Event Streaming Demonstration Completed Successfully!\n")


if __name__ == "__main__":
    run_day_32_demo()
