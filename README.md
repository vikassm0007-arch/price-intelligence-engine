<div align="center">

# 🕷️ Price Intelligence Engine & Web Scraping Foundations

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge)](./LICENSE)
[![Status](https://img.shields.io/badge/status-active_learning-orange.svg?style=for-the-badge)](#)

*Mastering web scraping, data extraction, and price intelligence engineering from first principles.*

[Quick Start](#-quick-start) • [Learning Curriculum](#-learning-curriculum) • [Target Mapping](#-target-mapping-reference) • [Scripts Roadmap](#-repository-structure)

---

</div>

## 📌 Overview

This repository documents the step-by-step journey of building a production-ready **Price Intelligence Engine**. It covers core HTTP request architectures, anti-bot bypass strategies, DOM tree parsing, multi-page crawling, defensive retries, deep product scraping, multi-threading, analytics generation, and structured dataset export using Python.

---

## 📅 Learning Curriculum

<details open>
<summary><b>Day 02 — HTTP Request Foundations</b> (<code>http_scraping_foundations.py</code>)</summary>

<br />

Core HTTP networking concepts required to reliably request raw web content without getting blocked (`requests.get`, User-Agent headers, status code validation).

</details>

<details open>
<summary><b>Day 03 — HTML Hierarchy & DOM Traversal</b> (<code>day_03_html_structure.py</code>)</summary>

<br />

Understanding HTML document architecture and locating target nodes inside nested DOM trees (`html` ➔ `head`, `body` ➔ `div`, `span`, `a`, `img`).

</details>

<details open>
<summary><b>Day 04 — BeautifulSoup Selectors</b> (<code>day_04_bs4_selectors.py</code>)</summary>

<br />

Mastering DOM search (`find`, `find_all`) and CSS selection (`select`, `select_one`) with modular extraction functions (`extract_title`, `extract_price`, `extract_url`).

</details>

<details open>
<summary><b>Day 05 — Build Your First Product Parser</b> (<code>day_05_product_parser.py</code>)</summary>

<br />

Transforming raw HTML cards into structured, typed product dictionary records (`name`, `price`, `currency`, `url`, `in_stock`).

</details>

<details open>
<summary><b>Day 06 — Pagination & Multi-Page Crawling</b> (<code>day_06_pagination.py</code>)</summary>

<br />

Automating multi-page product catalog crawling (`li.next > a`, `urljoin`, `time.sleep`).

</details>

<details open>
<summary><b>Day 07 — Data Cleaning, Normalization & Dataset Export</b> (<code>day_07_export_dataset.py</code>)</summary>

<br />

Cleaning, normalizing, and exporting extracted data into structured `products.json` and `products.csv` files.

</details>

<details open>
<summary><b>Day 08 — Defensive Scraping: Retries & User-Agent Rotation</b> (<code>day_08_defensive_scraping.py</code>)</summary>

<br />

Building fault-tolerant HTTP scrapers with `HTTPAdapter` retries, exponential backoff, and dynamic User-Agent rotation.

</details>

<details open>
<summary><b>Day 09 — Product Detail Page Scraping (Deep Crawling)</b> (<code>day_09_deep_product_scraper.py</code>)</summary>

<br />

Implementing two-stage deep product web scraping (Catalog List ➔ Detail Pages) extracting UPC codes, stock quantity, and category paths.

</details>

<details open>
<summary><b>Day 10 — Production Price Intelligence Engine Capstone</b> (<code>day_10_price_engine.py</code>)</summary>

<br />

A production-ready, multi-threaded Price Intelligence Engine:
* **Architecture**: Object-oriented `PriceIntelligenceEngine` class.
* **Concurrency**: `ThreadPoolExecutor` parallel worker pool for fast detail-page fetching.
* **Analytics**: Automated calculation of average price, min/max prices, stock percentages, and crawl duration.
* **Exports**: Comprehensive JSON (`price_intelligence_report.json`) and CSV (`price_intelligence_report.csv`) dataset reporting.

</details>

---

## ⚡ Quick Start

```bash
# 1. Install dependencies
pip install requests beautifulsoup4

# 2. Run Capstone Engine
python day_10_price_engine.py
```
