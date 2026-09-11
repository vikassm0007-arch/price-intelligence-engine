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

This repository documents the step-by-step journey of building a production-ready **Price Intelligence Engine**. It covers core HTTP request architectures, anti-bot bypass strategies, DOM tree parsing, multi-page crawling, defensive retries, deep product scraping, and structured dataset export using Python.

---

## 📅 Learning Curriculum

<details open>
<summary><b>Day 02 — HTTP Request Foundations</b> (<code>http_scraping_foundations.py</code>)</summary>

<br />

Core HTTP networking concepts required to reliably request raw web content without getting blocked:

* **GET Request Dispatching**: Fetching endpoints cleanly using `requests.get(url, headers=headers)`.
* **User-Agent Spoofing**: Crafting real-world browser headers to mimic desktop clients and avoid anti-scraping flags.
* **Status Code Handling**: Defensively handling responses across critical status bands (`200 OK`, `403 Forbidden`, `404 Not Found`, `500 Server Error`).
* **Payload Parsing (`.text` vs `.content`)**: `.text` for strings/HTML, `.content` for raw binary streams.

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

Building fault-tolerant HTTP scrapers:
* **Automatic Retries**: Configuring `HTTPAdapter` with exponential backoff strategy (`Retry` total=3, status_forcelist=[429, 500, 502, 503, 504]).
* **User-Agent Rotation**: Dynamically selecting real-world browser headers per request.
* **Safe Extraction**: Defensive DOM text extraction preventing `AttributeError` crashes on missing elements.

</details>

<details open>
<summary><b>Day 09 — Product Detail Page Scraping (Deep Crawling)</b> (<code>day_09_deep_product_scraper.py</code>)</summary>

<br />

Implementing two-stage deep product web scraping:
* **Stage 1 (Catalog List)**: Extract product detail URLs.
* **Stage 2 (Detail Page)**: Extract deep metadata including UPC / ISBN (`a897fe39b1...`), exact stock quantity (`22 available`), category breadcrumb paths (`Home > Books > Poetry`), and full descriptions.

</details>

---

## ⚡ Quick Start

```bash
# 1. Install dependencies
pip install requests beautifulsoup4

# 2. Run practice scripts
python http_scraping_foundations.py
python day_03_html_structure.py
python day_04_bs4_selectors.py
python day_05_product_parser.py
python day_06_pagination.py
python day_07_export_dataset.py
python day_08_defensive_scraping.py
python day_09_deep_product_scraper.py
```
