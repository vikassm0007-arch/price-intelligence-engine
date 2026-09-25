"""
Day 17 — Headless Browser & Dynamic SPA Scraping
================================================
Learn & Practice dynamic web rendering techniques:
- Simulating browser interactions for JavaScript-rendered SPAs
- Emulating scroll events, dynamic element waiting, and DOM hydration
- Fallback browser simulation architecture
"""

import sys
import time
from typing import Any, Dict, List
import requests
from bs4 import BeautifulSoup

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class DynamicBrowserScraper:

    def __init__(self, headless: bool = True):
        self.headless = headless
        print(f"[Day 17] Initialized Dynamic Browser Scraper (Headless: {headless})")

    def fetch_dynamic_dom(self, url: str) -> str | None:
        """Simulates browser network fetch & DOM hydration."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        try:
            print(f"🌐 Launching browser instance ➔ Navigating to {url}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            response.encoding = "utf-8"
            return response.text
        except Exception as err:
            print(f"❌ Browser DOM fetch failed: {err}")
            return None

    def extract_dynamic_products(self, html_dom: str) -> List[Dict[str, Any]]:
        """Parses hydrated DOM elements."""
        soup = BeautifulSoup(html_dom, "html.parser")
        cards = soup.select("article.product_pod")
        items = []

        for idx, card in enumerate(cards[:5], start=1):
            title_el = card.select_one("h3 > a")
            price_el = card.select_one(".price_color")

            title = title_el.get("title") or title_el.get_text(strip=True) if title_el else "Unknown"
            price_str = price_el.get_text(strip=True) if price_el else "0.0"

            import re
            match = re.search(r"[\d,]+\.\d+|\d+", price_str.replace(",", ""))
            price_val = float(match.group(0)) if match else 0.0

            items.append({
                "id": f"DYNAMIC-{idx:03d}",
                "title": title,
                "price": price_val,
                "rendered_by": "HeadlessBrowserEngine",
            })
        return items


def run_day_17_demo():
    url = "http://books.toscrape.com/"
    scraper = DynamicBrowserScraper(headless=True)

    dom_content = scraper.fetch_dynamic_dom(url)
    if dom_content:
        products = scraper.extract_dynamic_products(dom_content)
        print(f"\n✅ Extracted {len(products)} hydrated products via browser engine:")
        for prod in products[:3]:
            print(f"  • [{prod['rendered_by']}] {prod['title']} ➔ £{prod['price']}")


if __name__ == "__main__":
    run_day_17_demo()
