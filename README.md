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

This repository documents the step-by-step journey of building a production-ready **Price Intelligence Engine**. It covers core HTTP request architectures, anti-bot bypass strategies, DOM tree parsing, and structured data collection using Python.

---

## 📅 Learning Curriculum

<details open>
<summary><b>Day 02 — HTTP Request Foundations</b> (<code>http_scraping_foundations.py</code>)</summary>

<br />

Core HTTP networking concepts required to reliably request raw web content without getting blocked:

* **GET Request Dispatching**: Fetching endpoints cleanly using `requests.get(url, headers=headers)`.
* **User-Agent Spoofing**: Crafting real-world browser headers to mimic desktop clients and avoid anti-scraping flags.
* **Status Code Handling**: Defensively handling responses across critical status bands:
  * `200 OK` — Successful data payload.
  * `403 Forbidden` — Access restricted / Bot block detected.
  * `404 Not Found` — Endpoint non-existent.
  * `500 Internal Server Error` — Remote server breakdown.
* **Payload Parsing (`.text` vs `.content`)**:
  * `.text`: Decoded Unicode string for HTML, XML, and JSON responses.
  * `.content`: Raw binary response for media, images, and PDF streams.

</details>

<details open>
<summary><b>Day 03 — HTML Hierarchy & DOM Traversal</b> (<code>day_03_html_structure.py</code>)</summary>

<br />

Understanding HTML document architecture and locating target nodes inside nested DOM trees:

```text
HTML
 ├── html
 ├── head
 └── body
      ├── div
      ├── span
      ├── a
      └── img
```

* **`<html>`**: Root element wrapping the webpage.
* **`<head>`**: Contains metadata, page title, and stylesheet links.
* **`<body>`**: Encloses all visible webpage hierarchy.
* **`<div>` / `<span>`**: Organizational containers.
* **`<a>` / `<img>`**: Links and media elements.

</details>

<details open>
<summary><b>Day 04 — BeautifulSoup Selectors</b> (<code>day_04_bs4_selectors.py</code>)</summary>

<br />

Mastering DOM search & CSS selection methods for targeted data extraction:

* **DOM Searching**: `find()` & `find_all()`
* **CSS Selectors**: `select_one()` & `select()`
* **Selector Targets**: Classes (`.price_color`), Tags (`h3 > a`), Attributes (`[title]`)

```python
def extract_title(soup):
    link = soup.select_one("h3 > a")
    return link.get("title") if link else "N/A"

def extract_price(soup):
    price_el = soup.select_one(".price_color")
    return price_el.get_text(strip=True) if price_el else "N/A"

def extract_url(soup):
    link = soup.select_one("h3 > a")
    return link["href"] if link else "N/A"
```

</details>

<details open>
<summary><b>Day 05 — Build Your First Product Parser</b> (<code>day_05_product_parser.py</code>)</summary>

<br />

Building a production-ready pipeline that transforms raw unstructured HTML into clean, typed product data models:

```text
HTML ➔ BeautifulSoup ➔ Product Parser ➔ Product Dictionary
```

**Target Product Model**:
```python
product = {
    "name": "A Light in the Attic",
    "price": 51.77,
    "currency": "GBP",
    "url": "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
    "image_url": "http://books.toscrape.com/media/cache/2c/da/...jpg",
    "in_stock": True
}
```

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
```
