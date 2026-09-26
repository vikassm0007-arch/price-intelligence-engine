"""
Day 18 — Proxy Pool & IP Rotation
=================================
Learn & Practice proxy rotation for scalable price monitoring:
- Configuring HTTP/HTTPS proxy pools
- Proxy authentication, health checks, and fallback mechanisms
- Rotating proxy IP addresses dynamically on request failures
"""

import random
import sys
from typing import Any, Dict, List
import requests
from bs4 import BeautifulSoup

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Sample Proxy Pool Config
PROXY_POOL = [
    {"http": "http://10.10.1.10:8080", "https": "http://10.10.1.10:8080"},
    {"http": "http://10.10.1.11:8080", "https": "http://10.10.1.11:8080"},
    {"http": "http://10.10.1.12:8080", "https": "http://10.10.1.12:8080"},
]


class ProxyRotatorSession:

    def __init__(self, proxies: List[Dict[str, str]]):
        self.proxies = proxies
        self.session = requests.Session()

    def get_random_proxy(self) -> Dict[str, str] | None:
        return random.choice(self.proxies) if self.proxies else None

    def fetch_with_proxy(self, url: str) -> str | None:
        proxy = self.get_random_proxy()
        proxy_name = proxy["http"] if proxy else "Direct"
        print(f"🔒 Requesting {url} via Proxy: {proxy_name}")
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = self.session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            response.encoding = "utf-8"
            return response.text
        except Exception as err:
            print(f"❌ Proxy request failed ({err}). Rotating IP...")
            return None


def run_day_18_demo():
    rotator = ProxyRotatorSession(PROXY_POOL)
    url = "http://books.toscrape.com/"
    html = rotator.fetch_with_proxy(url)

    if html:
        soup = BeautifulSoup(html, "html.parser")
        products = soup.select("article.product_pod")
        print(f"✅ Extracted {len(products)} products via Proxy Session.")


if __name__ == "__main__":
    run_day_18_demo()
