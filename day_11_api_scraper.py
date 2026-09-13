"""
Day 11 — Dynamic Content & API Endpoint Inspection
===================================================
Learn & Practice extracting data from dynamic API endpoints:
- Fetching structured JSON payloads directly from REST/XHR endpoints
- Parsing API JSON responses into strongly typed product records
- Hybrid Scraper: Attempting direct API extraction first, falling back to HTML parsing
"""

import sys
from typing import Any, Dict, List
import requests
from bs4 import BeautifulSoup

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def fetch_api_products(api_endpoint: str) -> List[Dict[str, Any]] | None:
    """
    Attempts to fetch structured product data directly from a JSON API endpoint.
    Returns list of parsed product dicts if successful, or None if endpoint fails.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json, text/plain, */*",
    }
    try:
        response = requests.get(api_endpoint, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()

        # Parse JSON structure into standardized product models
        products = []
        items = data.get("products") or data.get("items") or (data if isinstance(data, list) else [])

        for item in items:
            products.append({
                "id": str(item.get("id") or item.get("upc") or "N/A"),
                "name": item.get("title") or item.get("name") or "Unknown",
                "price": float(item.get("price") or 0.0),
                "currency": item.get("currency") or "USD",
                "source": "API",
            })
        return products
    except (requests.exceptions.RequestException, ValueError) as err:
        print(f"⚠️ Direct API request unfulfilled ({err}). Switching to HTML fallback...")
        return None


def fetch_html_fallback(html_url: str) -> List[Dict[str, Any]]:
    """
    Fallback extractor: Scrapes product data from HTML markup when JSON API is unavailable.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(html_url, headers=headers, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.select("article.product_pod")
    products = []

    for idx, card in enumerate(cards[:5], start=1):
        title_el = card.select_one("h3 > a")
        price_el = card.select_one(".price_color")

        name = title_el.get("title") or title_el.get_text(strip=True) if title_el else "Unknown"
        price_text = price_el.get_text(strip=True) if price_el else "0.0"

        # Clean numerical price
        import re
        match = re.search(r"[\d,]+\.\d+|\d+", price_text.replace(",", ""))
        price_val = float(match.group(0)) if match else 0.0

        products.append({
            "id": f"ITEM-{idx:03d}",
            "name": name,
            "price": price_val,
            "currency": "GBP" if "£" in price_text else "USD",
            "source": "HTML_FALLBACK",
        })

    return products


def run_hybrid_scraper(api_url: str, fallback_html_url: str) -> List[Dict[str, Any]]:
    print(f"[Day 11] Running Hybrid Scraper (API Endpoint ➔ HTML Fallback)...\n")

    # Step 1: Try direct JSON API extraction first
    print(f"🌐 Attempting direct API extraction: {api_url}")
    products = fetch_api_products(api_url)

    # Step 2: Fallback to HTML parsing if API fails or returns empty
    if not products:
        print(f"📄 Scraping HTML markup fallback: {fallback_html_url}")
        products = fetch_html_fallback(fallback_html_url)

    print(f"\nSuccessfully collected {len(products)} products via {products[0]['source']} pipeline.\n")
    print("--- Sample Records ---")
    for prod in products[:3]:
        print(f"  • [{prod['source']}] {prod['id']}: {prod['name']} - {prod['currency']} {prod['price']}")

    return products


if __name__ == "__main__":
    # Test fallback flow on books.toscrape.com
    run_hybrid_scraper(
        api_url="http://books.toscrape.com/api/v1/products.json",
        fallback_html_url="http://books.toscrape.com/",
    )
