"""
Day 13 — Asynchronous High-Performance Scraping (asyncio & aiohttp)
===================================================================
Learn & Practice non-blocking asynchronous web scraping:
- Using aiohttp.ClientSession for async HTTP GET requests
- Gathering concurrent requests with asyncio.gather()
- Non-blocking HTML parsing with BeautifulSoup
- Performance benchmarking: Synchronous vs Asynchronous throughput
"""

import asyncio
import re
import sys
import time
from typing import Any, Dict, List
from urllib.parse import urljoin
import aiohttp
from bs4 import BeautifulSoup

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


async def fetch_page_async(session: aiohttp.ClientSession, url: str) -> str | None:
    """Asynchronously fetches a URL and returns raw HTML text."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
            response.raise_for_status()
            return await response.text(encoding="utf-8")
    except Exception as err:
        print(f"❌ Async fetch error for {url}: {err}")
        return None


def parse_product_html(html_content: str, url: str) -> Dict[str, Any] | None:
    """Parses product detail HTML into a structured dictionary."""
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, "html.parser")
    title_el = soup.select_one(".product_main h1")
    price_el = soup.select_one(".product_main .price_color")

    title = title_el.get_text(strip=True) if title_el else "Unknown"
    price_str = price_el.get_text(strip=True) if price_el else "0.0"

    match = re.search(r"[\d,]+\.\d+|\d+", price_str.replace(",", ""))
    price_val = float(match.group(0)) if match else 0.0

    return {
        "title": title,
        "price": price_val,
        "currency": "GBP" if "£" in price_str else "USD",
        "url": url,
    }


async def scrape_detail_pages_async(urls: List[str]) -> List[Dict[str, Any]]:
    """Fetches multiple product detail pages concurrently using asyncio.gather."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_page_async(session, url) for url in urls]
        html_results = await asyncio.gather(*tasks)

        products = []
        for html, url in zip(html_results, urls):
            if html:
                item = parse_product_html(html, url)
                if item:
                    products.append(item)
        return products


async def run_day_13_demo(catalog_url: str = "http://books.toscrape.com/", max_items: int = 10):
    print(f"[Day 13] Running Asynchronous High-Performance Scraper (asyncio + aiohttp)...\n")

    # Step 1: Fetch Catalog Page to get Detail URLs
    async with aiohttp.ClientSession() as session:
        catalog_html = await fetch_page_async(session, catalog_url)

    if not catalog_html:
        print("Failed to fetch catalog page.")
        return

    soup = BeautifulSoup(catalog_html, "html.parser")
    links = soup.select("article.product_pod h3 > a")[:max_items]
    detail_urls = [urljoin(catalog_url, link["href"]) for link in links]

    print(f"🚀 Discovered {len(detail_urls)} detail URLs. Starting async concurrent fetches...\n")

    start_time = time.time()
    products = await scrape_detail_pages_async(detail_urls)
    elapsed_time = round(time.time() - start_time, 2)

    print(f"⚡ Successfully scraped {len(products)} products in {elapsed_time}s!")
    print(f"📊 Throughput: {round(len(products) / elapsed_time, 2)} requests/sec\n")

    print("--- Sample Asynchronously Scraped Items ---")
    for prod in products[:3]:
        print(f"  • {prod['title']} ➔ £{prod['price']}")


if __name__ == "__main__":
    asyncio.run(run_day_13_demo())
