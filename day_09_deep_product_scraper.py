"""
Day 09 — Product Detail Page Scraping (Deep Crawling)
=====================================================
Learn & Practice two-stage deep product web scraping:
- Stage 1: Catalog List Page ➔ Extract product detail URLs
- Stage 2: Product Detail Page ➔ Extract deep metadata (UPC, Stock Count, Category, Description)
- Merging summary catalog info with deep product specifications
"""

import re
import sys
from typing import Any, Dict, List
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def parse_detail_table(soup: BeautifulSoup) -> Dict[str, str]:
    """Parses product specification table into a key-value dictionary."""
    specs = {}
    rows = soup.select("table.table-striped tr")
    for row in rows:
        header = row.select_one("th")
        value = row.select_one("td")
        if header and value:
            key = header.get_text(strip=True).lower().replace(" ", "_")
            specs[key] = value.get_text(strip=True)
    return specs


def extract_category_breadcrumbs(soup: BeautifulSoup) -> List[str]:
    """Extracts category hierarchy from breadcrumb navigation."""
    items = soup.select("ul.breadcrumb li a")
    return [item.get_text(strip=True) for item in items]


def parse_product_detail(detail_url: str, session: requests.Session) -> Dict[str, Any]:
    """
    Stage 2: Fetches and parses a single product detail page for deep metadata.
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = session.get(detail_url, headers=headers, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")

    # Title & Price
    title_el = soup.select_one(".product_main h1")
    title = title_el.get_text(strip=True) if title_el else "Unknown Title"

    price_el = soup.select_one(".product_main .price_color")
    price_str = price_el.get_text(strip=True) if price_el else "0.0"
    match = re.search(r"[\d,]+\.\d+|\d+", price_str.replace(",", ""))
    price_val = float(match.group(0)) if match else 0.0

    # Stock quantity from availability text e.g. 'In stock (22 available)'
    availability_el = soup.select_one(".product_main .instock.availability")
    avail_text = availability_el.get_text(strip=True) if availability_el else ""
    stock_match = re.search(r"\((\d+)\s+available\)", avail_text)
    stock_quantity = int(stock_match.group(1)) if stock_match else (1 if "in stock" in avail_text.lower() else 0)

    # Product Description
    desc_header = soup.select_one("#product_description")
    description = ""
    if desc_header:
        desc_p = desc_header.find_next_sibling("p")
        description = desc_p.get_text(strip=True) if desc_p else ""

    # Specification Table (UPC, Tax, Reviews)
    specs = parse_detail_table(soup)
    breadcrumbs = extract_category_breadcrumbs(soup)

    deep_product_record = {
        "upc": specs.get("upc", "N/A"),
        "title": title,
        "price": price_val,
        "currency": "GBP" if "£" in price_str else "UNKNOWN",
        "stock_quantity": stock_quantity,
        "category_path": " > ".join(breadcrumbs),
        "product_type": specs.get("product_type", "Books"),
        "number_of_reviews": int(specs.get("number_of_reviews", 0)),
        "description": description[:150] + "..." if len(description) > 150 else description,
        "detail_url": detail_url,
    }

    return deep_product_record


def run_day_09_demo(catalog_url: str = "http://books.toscrape.com/", max_items: int = 3):
    print(f"[Day 09] Running Two-Stage Deep Product Scraper on: {catalog_url}\n")
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0"}

    # Stage 1: Fetch Catalog List Page
    response = session.get(catalog_url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    product_links = soup.select("article.product_pod h3 > a")
    print(f"Stage 1: Found {len(product_links)} product links. Scraping top {max_items} detail pages...\n")

    deep_products = []
    for idx, link in enumerate(product_links[:max_items], start=1):
        detail_url = urljoin(catalog_url, link["href"])
        print(f"Stage 2 [{idx}/{max_items}]: Fetching Deep Metadata ➔ {detail_url}")
        record = parse_product_detail(detail_url, session)
        deep_products.append(record)

    print(f"\nSuccessfully collected {len(deep_products)} deep product records!\n")
    print("--- Sample Deep Product Record ---")
    import json
    print(json.dumps(deep_products[0], indent=2))

    return deep_products


if __name__ == "__main__":
    run_day_09_demo()
