"""
Lesson 2: HTML Structure & Element Parsing with BeautifulSoup
=============================================================

This script demonstrates how to parse an HTML document, navigate the DOM tree,
and extract target data (Title, Price, Product URL, Image URL) from books.toscrape.com.
"""

import sys
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

# Ensure Windows stdout handles UTF-8 encoding properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def scrape_books(base_url: str = "http://books.toscrape.com/"):
    """
    Fetches books.toscrape.com homepage, parses the product cards,
    and extracts Title, Price, Product URL, and Image URL.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    print(f"Fetching page: {base_url}")
    response = requests.get(base_url, headers=headers, timeout=10)
    response.raise_for_status()
    
    # Ensure correct response text encoding for currency symbols (£)
    response.encoding = "utf-8"

    # Create BeautifulSoup parsing object (DOM Tree)
    soup = BeautifulSoup(response.text, "html.parser")

    # Locate all product containers (<article class="product_pod">)
    product_cards = soup.find_all("article", class_="product_pod")
    print(f"Found {len(product_cards)} products on the page.\n")

    books_data = []

    for index, card in enumerate(product_cards[:5], start=1):  # First 5 items
        # 1. Product Title (lives inside <a title="..."> or <h3><a> text)
        title_tag = card.h3.find("a")
        title = title_tag.get("title") or title_tag.text.strip()

        # 2. Price (lives in inner text of <p class="price_color">)
        price_tag = card.find("p", class_="price_color")
        price = price_tag.text.strip() if price_tag else "N/A"

        # 3. Product URL (lives in 'href' attribute of <a> tag)
        relative_product_url = title_tag.get("href")
        full_product_url = urljoin(base_url, relative_product_url)

        # 4. Image URL (lives in 'src' attribute of <img> tag)
        img_tag = card.find("img")
        relative_img_url = img_tag.get("src") if img_tag else ""
        full_img_url = urljoin(base_url, relative_img_url)

        book_info = {
            "title": title,
            "price": price,
            "product_url": full_product_url,
            "image_url": full_img_url,
        }
        books_data.append(book_info)

        print(f"--- Book #{index} ---")
        print(f"📌 Title:       {title}")
        print(f"💵 Price:       {price}")
        print(f"🔗 Product URL: {full_product_url}")
        print(f"🖼️ Image URL:   {full_img_url}\n")

    return books_data


if __name__ == "__main__":
    scrape_books()
