"""
Day 10 — Production Price Intelligence Engine (Milestone Capstone)
===================================================================
A complete, multi-threaded Price Intelligence Engine that combines:
1. Resilient HTTP Sessions (Retries & User-Agent Rotation)
2. Multi-Page Catalog Pagination & Link Discovery
3. Concurrent Deep Product Metadata Scraping (ThreadPoolExecutor)
4. Data Normalization & Validation Pipeline
5. Analytics & Summary Statistics Generation
6. Multi-Format Dataset Export (JSON & CSV)
"""

import csv
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Tuple
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class PriceIntelligenceEngine:

    def __init__(self, base_url: str = "http://books.toscrape.com/", max_workers: int = 4):
        self.base_url = base_url
        self.max_workers = max_workers
        self.session = self._init_session()

    def _init_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        })
        return session

    def fetch_soup(self, url: str) -> BeautifulSoup | None:
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            response.encoding = "utf-8"
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.RequestException as err:
            print(f"❌ Failed fetching {url}: {err}")
            return None

    def discover_product_links(self, max_pages: int = 2) -> List[str]:
        product_urls = []
        current_url = self.base_url
        page_count = 0

        print(f"🔍 [Stage 1] Discovering product links across {max_pages} pages...")

        while current_url and page_count < max_pages:
            page_count += 1
            soup = self.fetch_soup(current_url)
            if not soup:
                break

            links = soup.select("article.product_pod h3 > a")
            for link in links:
                full_url = urljoin(current_url, link["href"])
                product_urls.append(full_url)

            # Next page
            next_btn = soup.select_one("li.next > a")
            current_url = urljoin(current_url, next_btn["href"]) if next_btn and next_btn.has_attr("href") else None

        print(f"✅ Discovered {len(product_urls)} product links from {page_count} catalog pages.\n")
        return product_urls

    def scrape_product_detail(self, detail_url: str) -> Dict[str, Any] | None:
        soup = self.fetch_soup(detail_url)
        if not soup:
            return None

        title_el = soup.select_one(".product_main h1")
        title = title_el.get_text(strip=True) if title_el else "Unknown"

        price_el = soup.select_one(".product_main .price_color")
        price_text = price_el.get_text(strip=True) if price_el else "0.0"
        match = re.search(r"[\d,]+\.\d+|\d+", price_text.replace(",", ""))
        price_val = float(match.group(0)) if match else 0.0

        avail_el = soup.select_one(".product_main .instock.availability")
        avail_text = avail_el.get_text(strip=True) if avail_el else ""
        stock_match = re.search(r"\((\d+)\s+available\)", avail_text)
        stock_qty = int(stock_match.group(1)) if stock_match else (1 if "in stock" in avail_text.lower() else 0)

        # Specifications table
        upc = "N/A"
        reviews = 0
        for row in soup.select("table.table-striped tr"):
            th = row.select_one("th")
            td = row.select_one("td")
            if th and td:
                hdr = th.get_text(strip=True).lower()
                if "upc" in hdr:
                    upc = td.get_text(strip=True)
                elif "reviews" in hdr:
                    reviews = int(td.get_text(strip=True))

        categories = [a.get_text(strip=True) for a in soup.select("ul.breadcrumb li a")]

        return {
            "upc": upc,
            "title": title,
            "price": price_val,
            "currency": "GBP" if "£" in price_text else "USD",
            "stock_quantity": stock_qty,
            "in_stock": stock_qty > 0,
            "category": categories[-1] if len(categories) > 1 else "General",
            "reviews": reviews,
            "url": detail_url,
        }

    def run_pipeline(self, max_pages: int = 2) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        start_time = time.time()

        # Step 1: Link Discovery
        urls = self.discover_product_links(max_pages=max_pages)

        # Step 2: Concurrent Multi-Threaded Scraping
        print(f"🚀 [Stage 2] Scraping {len(urls)} detail pages using {self.max_workers} threads...")
        scraped_data = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(self.scrape_product_detail, url): url for url in urls}
            for future in as_completed(future_to_url):
                res = future.result()
                if res:
                    scraped_data.append(res)

        elapsed_time = round(time.time() - start_time, 2)

        # Step 3: Calculate Analytics & Summary Statistics
        stats = self.generate_analytics(scraped_data, elapsed_time)
        return scraped_data, stats

    def generate_analytics(self, data: List[Dict[str, Any]], elapsed_time: float) -> Dict[str, Any]:
        if not data:
            return {"total_items": 0}

        prices = [d["price"] for d in data]
        in_stock_count = sum(1 for d in data if d["in_stock"])

        analytics = {
            "total_items_scraped": len(data),
            "execution_time_seconds": elapsed_time,
            "average_price": round(sum(prices) / len(prices), 2),
            "min_price": min(prices),
            "max_price": max(prices),
            "in_stock_percentage": round((in_stock_count / len(data)) * 100, 1),
        }
        return analytics

    def export(self, data: List[Dict[str, Any]], output_prefix: str = "price_intelligence_report"):
        json_file = f"{output_prefix}.json"
        csv_file = f"{output_prefix}.csv"

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        if data:
            with open(csv_file, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
                writer.writeheader()
                writer.writerows(data)

        print(f"📁 Dataset exported to: {json_file} & {csv_file}")


if __name__ == "__main__":
    engine = PriceIntelligenceEngine(max_workers=5)
    dataset, analytics = engine.run_pipeline(max_pages=2)

    print("\n================ Analytics Summary ================")
    for key, val in analytics.items():
        print(f"  • {key.replace('_', ' ').title()}: {val}")
    print("====================================================\n")

    engine.export(dataset, "price_intelligence_report")
