"""
Day 5 — Build Your First Product Parser
=======================================
Pipeline:
  Raw HTML ➔ BeautifulSoup ➔ Product Parser ➔ Structured Product Dictionaries

Converts raw web elements into clean, structured product data models:
product = {
    "name": str,
    "price": float,
    "currency": str,
    "url": str,
    "image_url": str,
    "in_stock": bool
}
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


def parse_price(raw_price_str: str) -> tuple[float, str]:
    """
    Parses raw price strings like '£51.77' or '$19.99' or '₹1,499.00'
    into a numeric float value and currency code/symbol.
    """
    if not raw_price_str:
        return 0.0, "UNKNOWN"

    currency_symbols = {
        "£": "GBP",
        "$": "USD",
        "€": "EUR",
        "₹": "INR",
    }

    currency = "UNKNOWN"
    for symbol, code in currency_symbols.items():
        if symbol in raw_price_str:
            currency = code
            break

    # Extract numerical float value using regex
    numeric_match = re.search(r"[\d,]+\.\d+|\d+", raw_price_str.replace(",", ""))
    price_val = float(numeric_match.group(0)) if numeric_match else 0.0

    return price_val, currency


def parse_single_product(card_soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
    """
    Parses a single HTML product card element into a structured Product Dictionary model.
    """
    # 1. Extract Name
    title_el = card_soup.select_one("h3 > a")
    name = title_el.get("title") or title_el.get_text(strip=True) if title_el else "Unknown Product"

    # 2. Extract & Parse Price / Currency
    price_el = card_soup.select_one(".price_color")
    raw_price = price_el.get_text(strip=True) if price_el else ""
    price_value, currency = parse_price(raw_price)

    # 3. Extract URL
    url = urljoin(base_url, title_el["href"]) if title_el and title_el.has_attr("href") else base_url

    # 4. Extract Image URL
    img_el = card_soup.select_one(".image_container img")
    image_url = urljoin(base_url, img_el["src"]) if img_el and img_el.has_attr("src") else ""

    # 5. Extract Availability
    instock_el = card_soup.select_one(".instock.availability")
    in_stock = "in stock" in instock_el.get_text(strip=True).lower() if instock_el else False

    # Structured Product Model
    product_model: Dict[str, Any] = {
        "name": name,
        "price": price_value,
        "currency": currency,
        "url": url,
        "image_url": image_url,
        "in_stock": in_stock,
    }
    return product_model


def parse_html_to_products(html_content: str, base_url: str) -> List[Dict[str, Any]]:
    """
    Full Pipeline: Raw HTML ➔ BeautifulSoup ➔ Product Parser ➔ Structured Product Dictionaries
    """
    soup = BeautifulSoup(html_content, "html.parser")
    product_cards = soup.select("article.product_pod")

    parsed_products = [parse_single_product(card, base_url) for card in product_cards]
    return parsed_products


def run_day_05_demo(target_url: str = "http://books.toscrape.com/"):
    print(f"[Day 5] Running HTML ➔ BeautifulSoup ➔ Product Parser Pipeline on: {target_url}\n")
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(target_url, headers=headers, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"

    # Execute Parser Pipeline
    products = parse_html_to_products(response.text, target_url)

    print(f"Successfully parsed {len(products)} structured product records.\n")
    print("--- Sample Structured Product Objects (First 3) ---")
    for idx, prod in enumerate(products[:3], start=1):
        print(f"Product #{idx}: {prod}")

    return products


if __name__ == "__main__":
    run_day_05_demo()
