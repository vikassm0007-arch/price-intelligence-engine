"""
Day 16 — Production CLI Application & Configuration Management
================================================================
Learn & Practice building production Command Line Interfaces (CLI):
- Command line flag parsing using argparse (--url, --pages, --output-json, --output-csv)
- Configurable scraper behavior and verbose execution logging
- Structured data extraction and multi-format export
"""

import argparse
import csv
import json
import re
import sys
from typing import Any, Dict, List
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def parse_cli_arguments() -> argparse.Namespace:
    """Configures and parses command-line arguments for the Price Intelligence CLI."""
    parser = argparse.ArgumentParser(
        description="Price Intelligence Engine CLI - Automated E-Commerce Scraper & Analytics Tool"
    )
    parser.add_argument("--url", type=str, default="http://books.toscrape.com/", help="Target catalog URL")
    parser.add_argument("--pages", type=int, default=2, help="Number of catalog pages to scrape")
    parser.add_argument("--output-json", type=str, default="cli_output.json", help="Output JSON file path")
    parser.add_argument("--output-csv", type=str, default="cli_output.csv", help="Output CSV file path")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose execution logging")
    return parser.parse_args()


def run_cli_scraper(url: str, pages: int, verbose: bool = False) -> List[Dict[str, Any]]:
    """Runs catalog scraper according to CLI options."""
    headers = {"User-Agent": "Mozilla/5.0"}
    all_products = []
    current_url = url
    page_num = 0

    while current_url and page_num < pages:
        page_num += 1
        if verbose:
            print(f"[CLI Logging] Fetching Page {page_num}/{pages}: {current_url}")

        try:
            response = requests.get(current_url, headers=headers, timeout=10)
            response.raise_for_status()
            response.encoding = "utf-8"
        except Exception as err:
            print(f"❌ Error fetching {current_url}: {err}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select("article.product_pod")

        for idx, card in enumerate(cards, start=1):
            title_el = card.select_one("h3 > a")
            price_el = card.select_one(".price_color")
            img_el = card.select_one(".image_container img")

            title = title_el.get("title") or title_el.get_text(strip=True) if title_el else "Unknown"
            price_text = price_el.get_text(strip=True) if price_el else "0.0"

            match = re.search(r"[\d,]+\.\d+|\d+", price_text.replace(",", ""))
            price_val = float(match.group(0)) if match else 0.0

            prod_url = urljoin(current_url, title_el["href"]) if title_el and title_el.has_attr("href") else current_url
            img_url = urljoin(current_url, img_el["src"]) if img_el and img_el.has_attr("src") else ""

            all_products.append({
                "id": f"P-{len(all_products)+1:04d}",
                "title": title,
                "price": price_val,
                "currency": "GBP" if "£" in price_text else "USD",
                "product_url": prod_url,
                "image_url": img_url,
            })

        # Next page link
        next_btn = soup.select_one("li.next > a")
        current_url = urljoin(current_url, next_btn["href"]) if next_btn and next_btn.has_attr("href") else None

    if verbose:
        print(f"[CLI Logging] Successfully scraped {len(all_products)} total items.")

    return all_products


def export_cli_results(data: List[Dict[str, Any]], json_path: str, csv_path: str):
    """Exports CLI results to JSON and CSV files."""
    if json_path:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"📁 JSON saved to: {json_path}")

    if csv_path and data:
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
            writer.writeheader()
            writer.writerows(data)
        print(f"📊 CSV saved to:  {csv_path}")


def main():
    args = parse_cli_arguments()
    print("================ Price Intelligence CLI ================")
    print(f"  • Target URL:    {args.url}")
    print(f"  • Max Pages:     {args.pages}")
    print(f"  • Verbose Mode:  {args.verbose}")
    print("========================================================\n")

    products = run_cli_scraper(args.url, args.pages, args.verbose)
    export_cli_results(products, args.output_json, args.output_csv)


if __name__ == "__main__":
    main()
