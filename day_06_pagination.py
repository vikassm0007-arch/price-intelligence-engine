"""
Day 6 — Pagination & Multi-Page Crawling
========================================
Learn & Practice handling multi-page web pagination:
- Finding the 'Next' page link dynamically
- Constructing relative and absolute pagination URLs
- Rate limiting with delays (polite scraping)
- Aggregating products across multiple catalog pages
"""

import sys
import time
from typing import Any, Dict, List
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def extract_next_page_url(soup: BeautifulSoup, current_url: str) -> str | None:
    """
    Locates the 'Next' page link in the pagination controls (e.g. <li class="next"><a href="...">).
    Returns the absolute URL if present, or None if on the last page.
    """
    next_btn = soup.select_one("li.next > a")
    if next_btn and next_btn.has_attr("href"):
        relative_href = next_btn["href"]
        return urljoin(current_url, relative_href)
    return None


def parse_page_products(soup: BeautifulSoup, current_url: str) -> List[Dict[str, Any]]:
    """
    Extracts structured product records from a single catalog page.
    """
    product_cards = soup.select("article.product_pod")
    products = []

    for card in product_cards:
        title_el = card.select_one("h3 > a")
        price_el = card.select_one(".price_color")
        img_el = card.select_one(".image_container img")

        title = title_el.get("title") or title_el.get_text(strip=True) if title_el else "Unknown"
        price_text = price_el.get_text(strip=True) if price_el else "N/A"
        product_url = urljoin(current_url, title_el["href"]) if title_el and title_el.has_attr("href") else current_url
        img_url = urljoin(current_url, img_el["src"]) if img_el and img_el.has_attr("src") else ""

        products.append({
            "title": title,
            "price_raw": price_text,
            "product_url": product_url,
            "image_url": img_url,
        })

    return products


def crawl_catalog(start_url: str = "http://books.toscrape.com/", max_pages: int = 3, delay_seconds: float = 1.0) -> List[Dict[str, Any]]:
    """
    Crawls multiple catalog pages sequentially using pagination links.
    """
    all_products: List[Dict[str, Any]] = []
    current_url: str | None = start_url
    page_count = 0
    headers = {"User-Agent": "Mozilla/5.0"}

    print(f"[Day 6] Starting pagination crawler on: {start_url} (Max pages: {max_pages})\n")

    while current_url and page_count < max_pages:
        page_count += 1
        print(f"📄 Fetching Page {page_count}: {current_url}")

        try:
            response = requests.get(current_url, headers=headers, timeout=10)
            response.raise_for_status()
            response.encoding = "utf-8"
        except requests.exceptions.RequestException as err:
            print(f"❌ Failed to fetch page {current_url}: {err}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        page_products = parse_page_products(soup, current_url)
        all_products.extend(page_products)
        print(f"   └── Found {len(page_products)} products on Page {page_count}.")

        # Find link to the next page
        current_url = extract_next_page_url(soup, current_url)

        if current_url and page_count < max_pages:
            print(f"   └── Pausing for {delay_seconds}s before requesting next page...")
            time.sleep(delay_seconds)

    print(f"\n✅ Crawl complete! Total products collected across {page_count} pages: {len(all_products)}\n")
    return all_products


if __name__ == "__main__":
    crawl_catalog(max_pages=3)
