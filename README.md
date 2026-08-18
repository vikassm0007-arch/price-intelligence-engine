# Web Scraping in Python: Complete Reference Guide

This repository contains lessons and working scripts covering the foundations of web scraping in Python.

---

## Lesson 1: HTTP Requests Basics
*See [`http_scraping_foundations.py`](./http_scraping_foundations.py)*

- **GET Requests:** Requesting data using `requests.get(url, headers=headers)`.
- **Status Codes:** Understanding `200 OK`, `403 Forbidden`, `404 Not Found`, and `500 Server Error`.
- **User-Agents:** Setting custom headers to emulate standard desktop web browsers.
- **`.text` vs `.content`:** Using `.text` for strings/HTML, and `.content` for raw bytes (images/PDFs).

---

## Lesson 2: HTML Structure & BeautifulSoup Parsing
*See [`html_structure_and_parsing.py`](./html_structure_and_parsing.py)*

### 1. HTML Hierarchy & DOM Tree
Web pages are structured as a tree of nested HTML tags:
- `<html>` → Root wrapper
  - `<head>` → Metadata and scripts
  - `<body>` → Visible page elements
    - `<article class="product_pod">` → Product card container
      - `<h3><a>` → Product title and link
      - `<p class="price_color">` → Price element
      - `<img>` → Image tag

### 2. Attributes vs. Inner Text
- **Inner Text**: Content placed between opening and closing tags.
  - Example: `<p class="price_color">£51.77</p>` → Extracted with `tag.text`
- **Attributes**: Key-value metadata inside the tag definition.
  - Example: `<a href="catalogue/book_1/index.html">` → Extracted with `tag['href']` or `tag.get('href')`
  - Example: `<img src="media/cover.jpg">` → Extracted with `tag['src']` or `tag.get('src')`

---

## Running the Practice Scripts

```bash
# Install required libraries
pip install requests beautifulsoup4

# Run Lesson 1 (HTTP Requests)
python http_scraping_foundations.py

# Run Lesson 2 (HTML Parsing Walkthrough)
python html_structure_and_parsing.py
```
