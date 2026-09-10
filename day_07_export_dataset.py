"""
Day 7 — Data Cleaning, Normalization & Dataset Export
=====================================================
Learn & Practice data pipelines:
- Normalizing raw web strings (cleaning text, extracting price float values)
- Converting rating text ('Three') to numeric integer ratings (3)
- Structuring clean dataset records
- Exporting dataset to JSON and CSV formats
"""

import csv
import json
import os
import re
import sys
from typing import Any, Dict, List
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RATING_MAP = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
}


def clean_price(raw_price_str: str) -> tuple[float, str]:
    """Cleans raw price string e.g. '£51.77' into float (51.77) and currency code ('GBP')."""
    if not raw_price_str:
        return 0.0, "UNKNOWN"

    currency = "GBP" if "£" in raw_price_str else ("USD" if "$" in raw_price_str else "UNKNOWN")
    match = re.search(r"[\d,]+\.\d+|\d+", raw_price_str.replace(",", ""))
    price_val = float(match.group(0)) if match else 0.0
    return price_val, currency


def clean_rating(card_soup: BeautifulSoup) -> int:
    """Extracts rating class e.g. 'star-rating Three' and converts to integer 3."""
    rating_tag = card_soup.select_one("p.star-rating")
    if not rating_tag or not rating_tag.has_attr("class"):
        return 0

    classes = [c.lower() for c in rating_tag["class"] if c.lower() != "star-rating"]
    if classes and classes[0] in RATING_MAP:
        return RATING_MAP[classes[0]]
    return 0


def build_clean_dataset(start_url: str = "http://books.toscrape.com/", max_items: int = 10) -> List[Dict[str, Any]]:
    """Fetches raw web products and applies normalization transformations."""
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(start_url, headers=headers, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.select("article.product_pod")
    dataset = []

    for card in cards[:max_items]:
        title_el = card.select_one("h3 > a")
        price_el = card.select_one(".price_color")
        img_el = card.select_one(".image_container img")

        title = title_el.get("title") or title_el.get_text(strip=True) if title_el else "Unknown"
        raw_price = price_el.get_text(strip=True) if price_el else ""
        price_val, currency = clean_price(raw_price)
        rating_val = clean_rating(card)

        product_url = urljoin(start_url, title_el["href"]) if title_el and title_el.has_attr("href") else start_url
        img_url = urljoin(start_url, img_el["src"]) if img_el and img_el.has_attr("src") else ""

        record = {
            "title": title,
            "price": price_val,
            "currency": currency,
            "rating": rating_val,
            "url": product_url,
            "image_url": img_url,
        }
        dataset.append(record)

    return dataset


def export_to_json(data: List[Dict[str, Any]], filepath: str) -> None:
    """Exports dataset to JSON format."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"📁 Exported {len(data)} items to JSON: {filepath}")


def export_to_csv(data: List[Dict[str, Any]], filepath: str) -> None:
    """Exports dataset to CSV format."""
    if not data:
        return

    fieldnames = list(data[0].keys())
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"📊 Exported {len(data)} items to CSV:  {filepath}")


def run_day_07_demo(output_dir: str = "."):
    print("[Day 7] Running Data Cleaning & Export Pipeline...\n")
    dataset = build_clean_dataset(max_items=5)

    json_path = os.path.join(output_dir, "products.json")
    csv_path = os.path.join(output_dir, "products.csv")

    export_to_json(dataset, json_path)
    export_to_csv(dataset, csv_path)

    print("\n--- Sample Cleaned Dataset Record ---")
    print(json.dumps(dataset[0], indent=2))


if __name__ == "__main__":
    run_day_07_demo()
