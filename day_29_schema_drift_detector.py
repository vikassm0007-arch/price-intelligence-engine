"""
Day 29 — Schema Drift Detection & Self-Healing Extraction Pipeline
===================================================================
Learn & Practice automated schema drift detection and self-healing web scrapers:
- Detecting website DOM restructuring and broken CSS selectors dynamically
- Calculating extraction confidence scores across scraping cycles
- Self-healing fallback extractors:
    1. Primary CSS Selectors
    2. Semantic Microdata (Schema.org / JSON-LD / OpenGraph)
    3. Structural & Regex Heuristics (pattern matching prices & product links)
- Generating Schema Drift Incident Reports for engineering alerts
"""

from datetime import datetime, timezone
import json
import re
import sys
from typing import Any, Dict, List, Optional
import requests
from bs4 import BeautifulSoup, Tag

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class SelfHealingProductParser:
    """Production parser equipped with multi-tier fallback strategies for schema drift."""

    def __init__(self):
        # Tier 1: Primary CSS Selectors (Assumed current schema)
        self.primary_selectors = {
            "container": "article.product_pod",
            "title": "h3 > a",
            "price": ".price_color",
            "link": "h3 > a",
        }

        # Incident log for detected drifts
        self.drift_incidents: List[Dict[str, Any]] = []

    def _extract_primary(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Tier 1: Extract items using primary CSS selectors."""
        cards = soup.select(self.primary_selectors["container"])
        if not cards:
            return []

        products = []
        for card in cards:
            title_el = card.select_one(self.primary_selectors["title"])
            price_el = card.select_one(self.primary_selectors["price"])

            title = title_el.get("title") or title_el.get_text(strip=True) if title_el else None
            price_text = price_el.get_text(strip=True) if price_el else None

            price = self._parse_price_number(price_text) if price_text else None

            if title and price is not None:
                products.append({
                    "title": title,
                    "price": price,
                    "extraction_tier": "PRIMARY_SELECTORS",
                })
        return products

    def _extract_microdata_or_json_ld(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Tier 2: Self-healing fallback using JSON-LD or Schema.org microdata."""
        products = []
        # Check for JSON-LD scripts
        json_ld_scripts = soup.find_all("script", type="application/ld+json")
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string or "{}")
                if isinstance(data, dict) and data.get("@type") == "Product":
                    products.append({
                        "title": data.get("name", "Unknown"),
                        "price": float(data.get("offers", {}).get("price", 0.0)),
                        "extraction_tier": "JSON_LD_MICRODATA",
                    })
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get("@type") == "Product":
                            products.append({
                                "title": item.get("name", "Unknown"),
                                "price": float(item.get("offers", {}).get("price", 0.0)),
                                "extraction_tier": "JSON_LD_MICRODATA",
                            })
            except Exception:
                continue

        # Check for Schema.org microdata attributes (itemprop)
        if not products:
            itemscope_elements = soup.find_all(attrs={"itemscope": True})
            for el in itemscope_elements:
                title_el = el.find(attrs={"itemprop": "name"})
                price_el = el.find(attrs={"itemprop": "price"})
                if title_el and price_el:
                    title = title_el.get_text(strip=True)
                    price = self._parse_price_number(price_el.get_text(strip=True))
                    if price is not None:
                        products.append({
                            "title": title,
                            "price": price,
                            "extraction_tier": "MICRODATA_ITEMPROP",
                        })
        return products

    def _extract_heuristics(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Tier 3: Self-healing fallback using structural regex and DOM density heuristics."""
        products = []
        # Find all currency symbols followed by decimals
        price_nodes = soup.find_all(string=re.compile(r"£\s*\d+\.\d{2}|\$\s*\d+\.\d{2}|€\s*\d+\.\d{2}"))

        for p_node in price_nodes:
            parent = p_node.find_parent(["article", "div", "li", "section"])
            if not parent:
                continue

            price_val = self._parse_price_number(str(p_node))
            if price_val is None:
                continue

            # Look for adjacent or ancestor heading / anchor tag for title
            heading = parent.find(["h1", "h2", "h3", "h4", "a"])
            title = None
            if heading:
                title = heading.get("title") or heading.get_text(strip=True)

            if title and len(title) > 2 and title != str(p_node).strip():
                # Avoid duplicates
                if not any(p["title"] == title for p in products):
                    products.append({
                        "title": title,
                        "price": price_val,
                        "extraction_tier": "STRUCTURAL_HEURISTICS",
                    })

        return products

    def _parse_price_number(self, text: str) -> Optional[float]:
        match = re.search(r"[\d,]+\.\d+|\d+", text.replace(",", ""))
        return float(match.group(0)) if match else None

    def parse(self, html_content: str, source_url: str = "") -> Dict[str, Any]:
        """Executes tiered extraction pipeline with drift detection and confidence scoring."""
        soup = BeautifulSoup(html_content, "html.parser")

        # 1. Try Primary
        products = self._extract_primary(soup)
        tier_used = "PRIMARY_SELECTORS"

        # 2. If Primary yielded 0 items, Schema Drift occurred! Trigger self-healing
        if not products:
            print("⚠️ [DRIFT DETECTED] Primary CSS selectors failed! Initiating self-healing engine...")

            # Tier 2: Microdata
            products = self._extract_microdata_or_json_ld(soup)
            if products:
                tier_used = "JSON_LD_MICRODATA"
            else:
                # Tier 3: Heuristics
                products = self._extract_heuristics(soup)
                if products:
                    tier_used = "STRUCTURAL_HEURISTICS"
                else:
                    tier_used = "EXTRACTION_FAILED"

            # Record drift incident
            incident = {
                "incident_type": "SCHEMA_DRIFT_WARNING",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source_url": source_url,
                "broken_selector": self.primary_selectors["container"],
                "fallback_strategy_activated": tier_used,
                "recovered_items_count": len(products),
            }
            self.drift_incidents.append(incident)

        # Compute Confidence Score
        confidence_score = 1.0 if tier_used == "PRIMARY_SELECTORS" and len(products) > 0 else (
            0.85 if tier_used == "JSON_LD_MICRODATA" else (
                0.70 if tier_used == "STRUCTURAL_HEURISTICS" and len(products) > 0 else 0.0
            )
        )

        return {
            "tier_used": tier_used,
            "confidence_score": confidence_score,
            "products_count": len(products),
            "products": products,
            "drift_detected": tier_used != "PRIMARY_SELECTORS",
        }


def run_day_29_demo():
    print("[Day 29] Running Schema Drift Detection & Self-Healing Pipeline...\n")
    parser = SelfHealingProductParser()

    # Case 1: Standard Catalog Page (Primary Selectors work normally)
    url = "http://books.toscrape.com/"
    print(f"--- Case 1: Scraping Baseline Page ({url}) ---")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = "utf-8"
        html = response.text
    except Exception as err:
        print(f"Network error: {err}")
        return

    result1 = parser.parse(html, source_url=url)
    print(f"✅ Strategy Used: {result1['tier_used']}")
    print(f"   └── Confidence Score: {result1['confidence_score'] * 100:.0f}%")
    print(f"   └── Products Extracted: {result1['products_count']}")
    if result1["products"]:
        sample = result1["products"][0]
        print(f"   └── Sample: '{sample['title']}' ➔ £{sample['price']}\n")

    # Case 2: Simulated Redesigned Website (Schema Drift: Changed class names)
    print("--- Case 2: Simulating Website Redesign (Drift Event) ---")
    simulated_redesigned_html = """
    <html>
        <body>
            <div class="store-inventory-grid">
                <div class="product-item-card-v2" itemscope itemtype="http://schema.org/Product">
                    <h2 class="item-header"><a href="/book/1" itemprop="name">The Pragmatic Programmer</a></h2>
                    <span class="price-badge-new" itemprop="price">£45.99</span>
                </div>
                <div class="product-item-card-v2" itemscope itemtype="http://schema.org/Product">
                    <h2 class="item-header"><a href="/book/2" itemprop="name">Designing Data-Intensive Applications</a></h2>
                    <span class="price-badge-new" itemprop="price">£52.50</span>
                </div>
                <div class="product-item-card-v2">
                    <h2 class="item-header"><a href="/book/3">Clean Code Architecture</a></h2>
                    <span class="price-tag-custom">£39.00</span>
                </div>
            </div>
        </body>
    </html>
    """

    result2 = parser.parse(simulated_redesigned_html, source_url="http://store.example.com/v2/catalog")
    print(f"🛡️ Self-Healing Strategy: {result2['tier_used']}")
    print(f"   └── Confidence Score: {result2['confidence_score'] * 100:.0f}%")
    print(f"   └── Recovered Items: {result2['products_count']}")
    for prod in result2["products"]:
        print(f"   • [{prod['extraction_tier']}] {prod['title']} ➔ £{prod['price']}")

    # Incident Report Output
    print("\n🚨 Schema Drift Incident Log:")
    print(json.dumps(parser.drift_incidents, indent=2))


if __name__ == "__main__":
    run_day_29_demo()
