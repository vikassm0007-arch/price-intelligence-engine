"""
Day 33 — Columnar Data Lake Ingestion: Partitioned Apache Parquet & Analytics
=============================================================================
Learn & Practice enterprise data lake ingestion for high-volume price intelligence:
- Scraping e-commerce catalog data and mapping to strongly-typed columnar formats
- Partitioned Lakehouse Storage (Hive-style partitioning: year/month/category)
- Parquet Compression (Snappy/GZIP): Achieving 80-90% storage reduction vs JSON/CSV
- Columnar Analytics: Fast vectorized queries (price percentiles, category aggregations)
"""

from datetime import datetime, timezone
import json
import os
import re
import shutil
import sys
import time
from typing import Any, Dict, List
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class ParquetLakehouseIngestor:
    """Manages ingestion of scraped datasets into a partitioned Parquet data lake."""

    def __init__(self, lakehouse_root: str = "datalake"):
        self.lakehouse_root = lakehouse_root
        os.makedirs(self.lakehouse_root, exist_ok=True)

    def write_partitioned_parquet(self, products: List[Dict[str, Any]]) -> str:
        """Converts products to a DataFrame and writes to partitioned Parquet files."""
        if not products:
            return ""

        df = pd.DataFrame(products)

        # Ensure typing
        df["price"] = df["price"].astype(float)
        df["in_stock"] = df["in_stock"].astype(bool)
        df["scraped_at"] = pd.to_datetime(df["scraped_at"])

        # Create partition columns
        df["year"] = df["scraped_at"].dt.year
        df["month"] = df["scraped_at"].dt.month

        # Write partitioned parquet
        output_path = os.path.join(self.lakehouse_root, "catalog_parquet")
        df.to_parquet(
            output_path,
            partition_cols=["year", "month", "category"],
            compression="snappy",
            index=False,
            engine="pyarrow",
        )
        return output_path

    def run_columnar_analytics(self) -> Dict[str, Any]:
        """Reads partitioned Parquet files and computes vectorized aggregations."""
        output_path = os.path.join(self.lakehouse_root, "catalog_parquet")
        if not os.path.exists(output_path):
            return {}

        df = pd.read_parquet(output_path, engine="pyarrow")

        # Vectorized category analytics
        category_stats = (
            df.groupby("category", observed=False)
            .agg(
                item_count=("price", "count"),
                avg_price=("price", "mean"),
                min_price=("price", "min"),
                max_price=("price", "max"),
                in_stock_rate=("in_stock", lambda s: round(s.mean() * 100, 1)),
            )
            .round(2)
            .to_dict(orient="index")
        )

        overall_metrics = {
            "total_records": len(df),
            "p50_median_price": round(float(df["price"].median()), 2),
            "p90_percentile_price": round(float(df["price"].quantile(0.90)), 2),
            "categories_monitored": df["category"].nunique(),
        }

        return {
            "overall": overall_metrics,
            "category_breakdown": category_stats,
        }


def scrape_catalog_dataset(url: str = "http://books.toscrape.com/") -> List[Dict[str, Any]]:
    """Scrapes live catalog with categories."""
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.select("article.product_pod")
    categories = ["Poetry", "Fiction", "Historical Fiction", "Mystery", "Philosophy"]

    scraped = []
    now_iso = datetime.now(timezone.utc).isoformat()

    for idx, card in enumerate(cards[:10], start=1):
        title_el = card.select_one("h3 > a")
        price_el = card.select_one(".price_color")

        title = title_el.get("title") or title_el.get_text(strip=True) if title_el else "Unknown"
        price_str = price_el.get_text(strip=True) if price_el else "0.0"

        match = re.search(r"[\d,]+\.\d+|\d+", price_str.replace(",", ""))
        price_val = float(match.group(0)) if match else 0.0

        scraped.append({
            "upc": f"LAKE-{idx:04d}",
            "title": title,
            "price": price_val,
            "category": categories[idx % len(categories)],
            "in_stock": True if idx % 4 != 0 else False,
            "scraped_at": now_iso,
        })

    return scraped


def run_day_33_demo():
    print("================================================================================")
    print("  Day 33 — Columnar Data Lake Ingestion: Partitioned Apache Parquet & Analytics")
    print("================================================================================\n")

    ingestor = ParquetLakehouseIngestor("datalake")

    # Step 1: Scrape Catalog
    print("🌐 Ingesting live catalog items...")
    dataset = scrape_catalog_dataset()
    print(f"✅ Extracted {len(dataset)} structured product records.\n")

    # Step 2: Write Partitioned Parquet Lakehouse
    print("📦 Writing partitioned Parquet files (Snappy compressed)...")
    parquet_path = ingestor.write_partitioned_parquet(dataset)
    print(f"✅ Lakehouse storage updated at: {parquet_path}\n")

    # Step 3: Run Vectorized Columnar Analytics
    print("📊 Executing Columnar OLAP Analytics on Parquet Lakehouse...")
    analytics = ingestor.run_columnar_analytics()

    print("\n--- Lakehouse Summary Metrics ---")
    for k, v in analytics["overall"].items():
        print(f"  • {k.replace('_', ' ').title()}: {v}")

    print("\n--- Category Breakdown Aggregations ---")
    print(json.dumps(analytics["category_breakdown"], indent=2))

    print("\n✅ Day 33 Lakehouse Ingestion Engine Completed Successfully!\n")


if __name__ == "__main__":
    run_day_33_demo()
