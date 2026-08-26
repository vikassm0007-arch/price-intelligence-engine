"""
Day 4 — BeautifulSoup Selectors
================================
Learn & Practice BeautifulSoup selection methods:
- find() vs find_all() (DOM element methods)
- select() vs select_one() (CSS selector methods)
- Understanding CSS Selectors: Classes (.class), IDs (#id), Attributes ([attr=val])
- Reusable modular extraction functions
"""

import sys
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def extract_title(card_soup: BeautifulSoup) -> str:
    """Extract product title using select_one with CSS selectors."""
    title_el = card_soup.select_one("h3 > a")
    if title_el:
        return title_el.get("title") or title_el.get_text(strip=True)
    return "N/A"


def extract_price(card_soup: BeautifulSoup) -> str:
    """Extract raw product price text using class selector."""
    price_el = card_soup.select_one(".price_color")
    return price_el.get_text(strip=True) if price_el else "N/A"


def extract_url(card_soup: BeautifulSoup, base_url: str = "http://books.toscrape.com/") -> str:
    """Extract full product URL from anchor tag href attribute."""
    link_el = card_soup.select_one("h3 > a")
    if link_el and link_el.has_attr("href"):
        return urljoin(base_url, link_el["href"])
    return "N/A"


def extract_image_url(card_soup: BeautifulSoup, base_url: str = "http://books.toscrape.com/") -> str:
    """Extract full image URL using img tag selector."""
    img_el = card_soup.select_one(".image_container img")
    if img_el and img_el.has_attr("src"):
        return urljoin(base_url, img_el["src"])
    return "N/A"


def run_day_04_demo(target_url: str = "http://books.toscrape.com/"):
    print(f"[Day 4] Demonstrating BeautifulSoup Selectors on: {target_url}\n")
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(target_url, headers=headers, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")

    # 1. find_all() vs select()
    cards_find_all = soup.find_all("article", class_="product_pod")
    cards_select = soup.select("article.product_pod")
    print(f"find_all() found: {len(cards_find_all)} cards")
    print(f"select()   found: {len(cards_select)} cards\n")

    # 2. Extract using reusable selector functions
    for idx, card in enumerate(cards_select[:3], start=1):
        print(f"--- Product #{idx} ---")
        print(f"📌 Title: {extract_title(card)}")
        print(f"💵 Price: {extract_price(card)}")
        print(f"🔗 URL:   {extract_url(card, target_url)}")
        print(f"🖼️ Image: {extract_image_url(card, target_url)}\n")


if __name__ == "__main__":
    run_day_04_demo()
