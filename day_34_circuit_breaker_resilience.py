"""
Day 34 — Resilient Web Scraping: Circuit Breaker Pattern & Fault Tolerance
==========================================================================
Learn & Practice high-availability fault tolerance for enterprise web scraping:
- Circuit Breaker State Machine: CLOSED ➔ OPEN ➔ HALF-OPEN
- Preventing IP subnet bans and resource exhaustion during target outages
- Fail-Fast Mechanism: Instant local failure when circuit is OPEN
- Automatic Cooldown & Canary Probes: Testing target recovery gracefully
- Stale-While-Revalidate Fallback: Serving cached catalog data during outages
"""

from datetime import datetime, timezone
from enum import Enum
import json
import sys
import time
from typing import Any, Callable, Dict, List, Optional
import requests
from bs4 import BeautifulSoup

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class CircuitState(str, Enum):
    CLOSED = "CLOSED"        # Normal operations: requests flow through
    OPEN = "OPEN"            # Outage detected: fail fast, block network calls
    HALF_OPEN = "HALF_OPEN"  # Testing recovery: single canary probe allowed


class CircuitBreakerOpenException(Exception):
    """Raised when an operation is attempted while the circuit breaker is OPEN."""
    pass


class CircuitBreaker:
    """Production Circuit Breaker with failure tracking and cooldown recovery."""

    def __init__(self, failure_threshold: int = 3, recovery_cooldown_seconds: float = 3.0):
        self.failure_threshold = failure_threshold
        self.cooldown = recovery_cooldown_seconds
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.last_state_change = time.time()

    def _check_state_transition(self):
        """Checks if OPEN circuit has rested enough to transition to HALF_OPEN."""
        if self.state == CircuitState.OPEN:
            elapsed = time.time() - (self.last_failure_time or 0.0)
            if elapsed >= self.cooldown:
                print(f"🔄 [Circuit Transition] Cooldown ({elapsed:.1f}s >= {self.cooldown}s) expired. Transitioning OPEN ➔ HALF_OPEN (Canary Mode).")
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = time.time()

    def record_success(self):
        """Records a successful network execution."""
        if self.state == CircuitState.HALF_OPEN:
            print("✅ [Circuit Transition] Canary probe succeeded! Transitioning HALF_OPEN ➔ CLOSED.")
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.last_state_change = time.time()
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def record_failure(self, error: Exception):
        """Records an execution failure and trips the circuit if threshold exceeded."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            print(f"❌ [Circuit Transition] Canary probe failed ({error})! Re-tripping HALF_OPEN ➔ OPEN.")
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()
        elif self.state == CircuitState.CLOSED and self.failure_count >= self.failure_threshold:
            print(f"🚨 [Circuit Transition] Consecutive failures ({self.failure_count}/{self.failure_threshold}) exceeded! Tripping CLOSED ➔ OPEN.")
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()

    def execute(self, func: Callable[[], Any], fallback_func: Optional[Callable[[], Any]] = None) -> Any:
        """Executes the wrapped function through the circuit breaker safety shield."""
        self._check_state_transition()

        if self.state == CircuitState.OPEN:
            print("🛡️ [Circuit Breaker: OPEN] Blocking network request to avoid IP ban. Failing fast!")
            if fallback_func:
                print("📦 [Fallback] Serving stale-while-revalidate cached dataset.")
                return fallback_func()
            raise CircuitBreakerOpenException("Circuit breaker is currently OPEN.")

        try:
            result = func()
            self.record_success()
            return result
        except Exception as err:
            self.record_failure(err)
            if fallback_func:
                print("📦 [Fallback on Failure] Serving cached catalog snapshot.")
                return fallback_func()
            raise


class ResilientPriceScraper:
    """Scraper fortified with a Circuit Breaker and Stale-While-Revalidate caching."""

    def __init__(self, target_url: str = "http://books.toscrape.com/"):
        self.target_url = target_url
        self.breaker = CircuitBreaker(failure_threshold=3, recovery_cooldown_seconds=2.0)
        self.cached_snapshot: List[Dict[str, Any]] = []
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

    def _scrape_network_call(self, simulate_outage: bool = False) -> List[Dict[str, Any]]:
        if simulate_outage:
            raise requests.exceptions.HTTPError("HTTP 503 Service Unavailable (Target Under Maintenance)")

        response = self.session.get(self.target_url, timeout=10)
        response.raise_for_status()
        response.encoding = "utf-8"

        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select("article.product_pod")

        items = []
        for idx, card in enumerate(cards[:4], start=1):
            title_el = card.select_one("h3 > a")
            price_el = card.select_one(".price_color")

            title = title_el.get("title") or title_el.get_text(strip=True) if title_el else "Unknown"
            price_str = price_el.get_text(strip=True) if price_el else "0.0"

            import re
            match = re.search(r"[\d,]+\.\d+|\d+", price_str.replace(",", ""))
            price_val = float(match.group(0)) if match else 0.0

            items.append({
                "upc": f"RESILIENT-{idx:03d}",
                "title": title,
                "price": price_val,
                "currency": "GBP",
            })

        self.cached_snapshot = items
        return items

    def scrape_catalog(self, simulate_outage: bool = False) -> Dict[str, Any]:
        """Scrapes catalog wrapped with circuit protection."""
        def make_request():
            return self._scrape_network_call(simulate_outage=simulate_outage)

        def serve_stale():
            return list(self.cached_snapshot)

        items = self.breaker.execute(make_request, fallback_func=serve_stale)
        return {
            "circuit_state": self.breaker.state.value,
            "items_count": len(items),
            "items": items,
        }


def run_day_34_demo():
    print("================================================================================")
    print("  Day 34 — Resilient Web Scraping: Circuit Breaker Pattern & Fault Tolerance")
    print("================================================================================\n")

    scraper = ResilientPriceScraper()

    # Phase 1: Normal Operations (Circuit CLOSED)
    print("--- Phase 1: Healthy Network Requests (Circuit CLOSED) ---")
    res1 = scraper.scrape_catalog(simulate_outage=False)
    print(f"✅ Success! Circuit State: {res1['circuit_state']} | Items extracted: {res1['items_count']}\n")

    # Phase 2: Target Website Outage (Tripping the Circuit Breaker)
    print("--- Phase 2: Simulating Target Outages (HTTP 503 Errors) ---")
    for attempt in range(1, 4):
        print(f"\n[Outage Attempt {attempt}]")
        scraper.scrape_catalog(simulate_outage=True)

    # Phase 3: Fast-Fail when Circuit is OPEN
    print("\n--- Phase 3: Fast-Fail Execution (Circuit OPEN) ---")
    res_open = scraper.scrape_catalog(simulate_outage=True)
    print(f"🛡️ Handled via Fallback: State: {res_open['circuit_state']} | Fallback records served: {res_open['items_count']}")

    # Phase 4: Cooldown & Automatic Recovery (HALF_OPEN ➔ CLOSED)
    print("\n--- Phase 4: Cooldown & Self-Healing Probe Recovery ---")
    print("Pausing 2.2 seconds for cooldown timer to expire...")
    time.sleep(2.2)

    print("\nSending canary probe request to healthy target...")
    res_recovered = scraper.scrape_catalog(simulate_outage=False)
    print(f"🎉 Fully Recovered! Final Circuit State: {res_recovered['circuit_state']} | Items: {res_recovered['items_count']}\n")

    print("✅ Day 34 Circuit Breaker Demonstration Completed Successfully!\n")


if __name__ == "__main__":
    run_day_34_demo()
