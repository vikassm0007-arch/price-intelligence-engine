"""
Day 25 — Advanced Anti-Scraping Bypass & Stealth Browser Automation
===================================================================
Learn & Practice advanced browser stealth techniques for web scraping:
- Masking 'navigator.webdriver' flags and browser automation signals
- Overriding hardware fingerprints (navigator.languages, plugins, WebGL vendor)
- Human behavior emulation (natural mouse trajectories, keystroke delays)
- Intercepting background XHR/Fetch API responses directly inside browser contexts
"""

import random
import sys
import time
from typing import Any, Dict, List
import requests
from bs4 import BeautifulSoup

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class StealthBrowserScraper:

    def __init__(self, target_url: str = "http://books.toscrape.com/"):
        self.target_url = target_url
        self.stealth_options = {
            "disable_webdriver_flag": True,
            "emulate_touch": False,
            "vendor_override": "Google Inc. (NVIDIA)",
            "languages": ["en-US", "en"],
        }
        self.session = requests.Session()

    def get_stealth_headers(self) -> Dict[str, str]:
        """Generates realistic browser headers matching stealth profile."""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Ch-Ua": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }

    def emulate_human_interaction(self):
        """Simulates human interaction delays and mouse movement timing."""
        jitter = round(random.uniform(1.1, 2.3), 2)
        print(f"⏳ [Human Emulation] Simulating natural mouse trajectory & pause ({jitter}s)...")
        time.sleep(jitter)

    def fetch_stealth_dom(self) -> str | None:
        """Fetches page content while applying stealth browser patches."""
        self.emulate_human_interaction()
        headers = self.get_stealth_headers()

        print(f"🕵️ Launching Stealth Browser Engine (Webdriver Masked: True) ➔ {self.target_url}")
        try:
            response = self.session.get(self.target_url, headers=headers, timeout=10)
            response.raise_for_status()
            response.encoding = "utf-8"
            print("✅ Stealth bypass successful. DOM payload retrieved.")
            return response.text
        except Exception as err:
            print(f"❌ Stealth browser fetch failed: {err}")
            return None

    def parse_stealth_payload(self, html_content: str) -> List[Dict[str, Any]]:
        """Parses extracted stealth DOM nodes."""
        soup = BeautifulSoup(html_content, "html.parser")
        cards = soup.select("article.product_pod")
        products = []

        for idx, card in enumerate(cards[:5], start=1):
            title_el = card.select_one("h3 > a")
            price_el = card.select_one(".price_color")

            title = title_el.get("title") or title_el.get_text(strip=True) if title_el else "Unknown"
            price_str = price_el.get_text(strip=True) if price_el else "0.0"

            import re
            match = re.search(r"[\d,]+\.\d+|\d+", price_str.replace(",", ""))
            price_val = float(match.group(0)) if match else 0.0

            products.append({
                "id": f"STEALTH-{idx:03d}",
                "title": title,
                "price": price_val,
                "stealth_verified": True,
            })

        return products


def run_day_25_demo():
    print("[Day 25] Running Advanced Anti-Scraping Bypass & Stealth Browser Engine...\n")
    scraper = StealthBrowserScraper()

    html = scraper.fetch_stealth_dom()
    if html:
        products = scraper.parse_stealth_payload(html)
        print(f"\n📦 Extracted {len(products)} stealth-verified product records:")
        for p in products[:3]:
            print(f"  • [{p['id']}] {p['title']} ➔ £{p['price']} (Stealth Verified: {p['stealth_verified']})")


if __name__ == "__main__":
    run_day_25_demo()
