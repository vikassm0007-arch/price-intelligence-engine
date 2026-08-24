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
  HTML (Root)
   ├── <html>
   │    ├── <head> ── [Metadata, Scripts, Styles]
   │    └── <body> ── [Visible Webpage Hierarchy]
   │         ├── <div class="product_pod"> ── [Card Container]
   │         │    ├── <p class="price_color"> ── [Price Fragment]
   │         │    ├── <a href="..."> ── [Product Link]
   │         │    └── <img src="..."> ── [Product Media]
