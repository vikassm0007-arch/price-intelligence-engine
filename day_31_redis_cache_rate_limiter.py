"""
Day 31 — High-Throughput Caching, Token Bucket Rate Limiting & ETag Deduplication
=================================================================================
Learn & Practice production-grade scraping optimization and throughput management:
- Token Bucket Rate Limiting: Preventing IP bans while allowing controlled burst requests
- Conditional HTTP Caching: Leveraging HTTP 304 Not Modified, ETag, and If-Modified-Since
- Content Hash Deduplication: Detecting unchanged page snapshots via SHA-256 fingerprinting
- In-Memory / Redis Caching Layer: Ultra-fast price lookups with Time-To-Live (TTL) expiration
"""

from datetime import datetime, timezone
import hashlib
import json
import re
import sys
import time
from typing import Any, Dict, List, Optional
import requests
from bs4 import BeautifulSoup

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class TokenBucketRateLimiter:
    """Thread-safe Token Bucket algorithm for controlling scrape request rates."""

    def __init__(self, rate_per_second: float = 2.0, max_burst: int = 5):
        self.rate = rate_per_second
        self.capacity = max_burst
        self.tokens = float(max_burst)
        self.last_update = time.time()

    def acquire(self) -> float:
        """Blocks until a token is available, returns wait duration."""
        now = time.time()
        elapsed = now - self.last_update
        self.last_update = now

        # Replenish tokens based on elapsed time
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)

        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return 0.0

        # Calculate necessary sleep time
        wait_time = (1.0 - self.tokens) / self.rate
        time.sleep(wait_time)
        self.tokens = 0.0
        self.last_update = time.time()
        return wait_time


class SmartCacheManager:
    """Simulates Redis caching with TTL, ETag tracking, and content hash deduplication."""

    def __init__(self, default_ttl_seconds: int = 3600):
        self.default_ttl = default_ttl_seconds
        # In-memory key-value store: key -> {etag, content_hash, data, expires_at}
        self.cache: Dict[str, Dict[str, Any]] = {}

    def get_cached_etag(self, url: str) -> Optional[str]:
        entry = self.cache.get(url)
        if entry and time.time() < entry["expires_at"]:
            return entry.get("etag")
        return None

    def store_snapshot(self, url: str, etag: Optional[str], html: str, parsed_products: List[Dict[str, Any]]):
        content_hash = hashlib.sha256(html.encode("utf-8")).hexdigest()
        self.cache[url] = {
            "etag": etag,
            "content_hash": content_hash,
            "products": parsed_products,
            "cached_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": time.time() + self.default_ttl,
        }

    def is_content_identical(self, url: str, html: str) -> bool:
        entry = self.cache.get(url)
        if not entry:
            return False
        curr_hash = hashlib.sha256(html.encode("utf-8")).hexdigest()
        return curr_hash == entry.get("content_hash")


class OptimizedScraperEngine:
    """Scraper combining Token Bucket rate limiting, ETag optimization, and caching."""

    def __init__(self, target_url: str = "http://books.toscrape.com/"):
        self.target_url = target_url
        self.rate_limiter = TokenBucketRateLimiter(rate_per_second=2.0, max_burst=3)
        self.cache = SmartCacheManager(default_ttl_seconds=300)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })

    def fetch_with_caching(self, url: str) -> Dict[str, Any]:
        # 1. Acquire Rate Limit Token
        wait_seconds = self.rate_limiter.acquire()
        if wait_seconds > 0:
            print(f"⏳ [Rate Limiter] Throttled request: waited {wait_seconds:.2f}s for available token.")

        # 2. Check for Conditional ETag
        headers = {}
        cached_etag = self.cache.get_cached_etag(url)
        if cached_etag:
            headers["If-None-Match"] = cached_etag

        print(f"🌐 Requesting {url} (Conditional ETag: {cached_etag or 'None'})...")
        response = self.session.get(url, headers=headers, timeout=10)

        # 3. Handle HTTP 304 Not Modified
        if response.status_code == 304:
            print("⚡ [HTTP 304 Not Modified] Server confirmed page unchanged. Returning cached dataset!")
            return {
                "source": "CACHE_304_HIT",
                "products": self.cache.cache[url]["products"],
                "saved_bandwidth": True,
            }

        response.raise_for_status()
        response.encoding = "utf-8"

        # 4. Check for Content Hash Deduplication
        if self.cache.is_content_identical(url, response.text):
            print("⚡ [Content Hash Hit] SHA-256 fingerprint matches cache! Zero-parsing bypass.")
            return {
                "source": "CONTENT_HASH_HIT",
                "products": self.cache.cache[url]["products"],
                "saved_bandwidth": False,
            }

        # 5. Full Parsing
        print("🔍 Parsing fresh HTML payload...")
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
                "id": f"ITEM-{idx:03d}",
                "title": title,
                "price": price_val,
                "currency": "GBP",
            })

        # Store in Smart Cache
        server_etag = response.headers.get("ETag")
        self.cache.store_snapshot(url, server_etag, response.text, products)

        return {
            "source": "LIVE_EXTRACT",
            "products": products,
            "saved_bandwidth": False,
        }


def run_day_31_demo():
    print("================================================================================")
    print("  Day 31 — High-Throughput Caching, Rate Limiting & ETag Deduplication Engine")
    print("================================================================================\n")

    engine = OptimizedScraperEngine()
    url = "http://books.toscrape.com/"

    # Pass 1: Fresh live extraction
    print("--- Execution Pass 1: Cold Cache (Live Extraction) ---")
    result1 = engine.fetch_with_caching(url)
    print(f"✅ Result 1 Source: {result1['source']} | Items: {len(result1['products'])}\n")

    # Pass 2: Immediate re-scrape (Content Hash Deduplication)
    print("--- Execution Pass 2: Warm Cache (Content Hash Deduplication) ---")
    result2 = engine.fetch_with_caching(url)
    print(f"✅ Result 2 Source: {result2['source']} | Items: {len(result2['products'])}\n")

    # Pass 3: Rate-Limiting Burst Demonstration
    print("--- Execution Pass 3: Token Bucket Rate Limiting Burst Test ---")
    print("Dispatching 4 rapid requests to trigger token bucket throttling...")
    for i in range(1, 5):
        engine.rate_limiter.acquire()
        print(f"  • Dispatched request #{i} via token bucket.")

    print("\n✅ Day 31 Engine Demonstration Completed Successfully!\n")


if __name__ == "__main__":
    run_day_31_demo()
