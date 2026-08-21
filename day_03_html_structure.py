"""
Day 3 — HTML Structure
======================
Learn & Practice HTML structure for web scraping:
- HTML DOM Hierarchy (html -> head, body -> div, span, a, img)
- Target Identification: Product title, Price, Product URL, Image URL
- Practice on permitted site: http://books.toscrape.com/
"""

import sys
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

# Ensure Windows stdout handles UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def parse_html_structure(base_url: str = "http://books.toscrape.com/"):
    """
    Fetches books.toscrape.com and extracts the 4 core product elements:
    1. Product Title
    2. Price
    3. Product URL
    4. Image URL
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    print(f"[Day 3] Fetching practice page: {base_url}")
    response = requests.get(base_url, headers=headers, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"

    # Parse HTML hierarchy
    soup = BeautifulSoup(response.text, "html.parser")

    # Target container element (<article class="product_pod">)
    products = soup.find_all("article", class_="product_pod")
    print(f"Found {len(products)} products on page.\n")

    results = []
    for idx, card in enumerate(products[:5], start=1):
        # Title tag (<a title="..."> inside <h3>)
        title_tag = card.h3.find("a")
        title = title_tag.get("title") or title_tag.text.strip()

        # Price tag (<p class="price_color">)
        price_tag = card.find("p", class_="price_color")
        price = price_tag.text.strip() if price_tag else "N/A"

        # Product URL (href attribute of <a>)
        product_url = urljoin(base_url, title_tag.get("href"))

        # Image URL (src attribute of <img>)
        img_tag = card.find("img")
        image_url = urljoin(base_url, img_tag.get("src")) if img_tag else "N/A"

        item = {
            "title": title,
            "price": price,
            "product_url": product_url,
            "image_url": image_url,
        }
        results.append(item)

        print(f"--- Product #{idx} ---")
        print(f"📌 Product Title: {title}")
        print(f"💵 Price:         {price}")
        print(f"🔗 Product URL:   {product_url}")
        print(f"🖼️ Image URL:     {image_url}\n")

    return results


if __name__ == "__main__":
    parse_html_structure()
