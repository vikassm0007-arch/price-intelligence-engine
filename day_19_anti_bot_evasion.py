"""
Day 19 — Anti-Bot Evasion & Request Fingerprinting Engine
==========================================================
Learn & Practice advanced anti-bot evasion techniques:
- Browser profile fingerprinting (Chrome, Firefox, Safari profile presets)
- Session cookie persistence & organic referrer chain navigation
- WAF / CAPTCHA challenge detection engine (Cloudflare, Akamai, DataDome signatures)
- Human request behavior simulation with variable delay jitter
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

# Real-world browser profiles with matching SEC headers and User-Agents
BROWSER_PROFILES = [
    {
        "name": "Chrome 122 Windows",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
        },
    },
    {
        "name": "Firefox 123 macOS",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
        },
    },
]


class AntiBotEvasionEngine:

    def __init__(self):
        self.session = requests.Session()
        self.current_profile = random.choice(BROWSER_PROFILES)
        self.last_url = ""

    def inspect_waf_challenges(self, response_text: str) -> List[str]:
        """Detects anti-bot WAF signature keywords in HTML response payload."""
        text_lower = response_text.lower()
        challenges_found = []

        if "cf-challenge" in text_lower or "just a moment..." in text_lower:
            challenges_found.append("Cloudflare Turnstile / Challenge")
        if "akamai" in text_lower or "access denied" in text_lower:
            challenges_found.append("Akamai Bot Manager")
        if "datadome" in text_lower:
            challenges_found.append("DataDome Security Shield")

        return challenges_found

    def fetch_page_organically(self, target_url: str) -> str | None:
        """Fetches a target page with human delay jitter, profile headers, and referrer context."""
        headers = dict(self.current_profile["headers"])
        if self.last_url:
            headers["Referer"] = self.last_url

        # Simulate human reading delay (1.0s to 2.2s jitter)
        delay = round(random.uniform(1.0, 2.2), 2)
        print(f"⏳ [Human Simulation] Pausing {delay}s | Profile: {self.current_profile['name']}")
        time.sleep(delay)

        print(f"🕵️ Dispatching organic GET request ➔ {target_url}")
        try:
            response = self.session.get(target_url, headers=headers, timeout=10)
            response.raise_for_status()
            response.encoding = "utf-8"

            self.last_url = target_url
            waf_issues = self.inspect_waf_challenges(response.text)

            if waf_issues:
                print(f"⚠️ WAF Challenges Detected: {', '.join(waf_issues)}")
            else:
                print("✅ Passed anti-bot fingerprint checks cleanly.")

            return response.text
        except Exception as err:
            print(f"❌ Organic fetch failed: {err}")
            return None


def run_day_19_demo():
    print("[Day 19] Running Enhanced Anti-Bot Evasion & Fingerprinting Engine...\n")
    engine = AntiBotEvasionEngine()

    url = "http://books.toscrape.com/"
    html = engine.fetch_page_organically(url)

    if html:
        soup = BeautifulSoup(html, "html.parser")
        products = soup.select("article.product_pod")
        print(f"\n📦 Successfully scraped {len(products)} products using organic browser session.")


if __name__ == "__main__":
    run_day_19_demo()
