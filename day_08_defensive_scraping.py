"""
Day 08 — Defensive Scraping: Retries, User-Agent Rotation & Error Resiliency
==========================================================================
Learn & Practice defensive scraping strategies for production resilience:
- Configuring HTTPAdapter with exponential backoff retries for 429/500/502/503/504
- Rotating User-Agent headers dynamically per request
- Defensive parsing with safe fallback extractors for missing DOM elements
- Timeout management and exception safety
"""

import random
import sys
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from bs4 import BeautifulSoup

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Real-world User-Agent pool for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]


def get_random_headers() -> dict[str, str]:
    """Returns HTTP headers with a randomly selected User-Agent."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }


def create_resilient_session(retries: int = 3, backoff_factor: float = 1.0) -> requests.Session:
    """
    Creates a requests.Session configured with automatic retries and exponential backoff
    for status codes 429, 500, 502, 503, 504.
    """
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def safe_extract_text(soup: BeautifulSoup, selector: str, default: str = "N/A") -> str:
    """Defensively extracts text from a CSS selector without throwing AttributeError."""
    element = soup.select_one(selector)
    return element.get_text(strip=True) if element else default


def fetch_with_resilience(url: str, session: requests.Session | None = None) -> str | None:
    """Fetches web page content using resilient sessions, dynamic headers, and timeouts."""
    if session is None:
        session = create_resilient_session()

    headers = get_random_headers()
    print(f"Fetching {url} using User-Agent: {headers['User-Agent'][:45]}...")

    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = "utf-8"
        return response.text
    except requests.exceptions.HTTPError as http_err:
        print(f"❌ HTTP Error for {url}: {http_err}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error for {url}")
    except requests.exceptions.Timeout:
        print(f"❌ Request Timeout for {url}")
    except requests.exceptions.RequestException as err:
        print(f"❌ Request Failed: {err}")

    return None


def run_day_08_demo(target_url: str = "http://books.toscrape.com/"):
    print("[Day 08] Demonstrating Defensive Scraping & Resilient Sessions...\n")
    session = create_resilient_session(retries=3, backoff_factor=0.5)

    html_content = fetch_with_resilience(target_url, session=session)
    if not html_content:
        print("Failed to retrieve content defensively.")
        return

    soup = BeautifulSoup(html_content, "html.parser")
    cards = soup.select("article.product_pod")

    print(f"\nSuccessfully parsed {len(cards)} product cards defensively.\n")
    for idx, card in enumerate(cards[:3], start=1):
        title = safe_extract_text(card, "h3 > a", default="Unknown Title")
        price = safe_extract_text(card, ".price_color", default="N/A")
        availability = safe_extract_text(card, ".instock.availability", default="Unknown")

        print(f"--- Product #{idx} ---")
        print(f"📌 Title:        {title}")
        print(f"💵 Price:        {price}")
        print(f"📦 Availability: {availability}\n")


if __name__ == "__main__":
    run_day_08_demo()
