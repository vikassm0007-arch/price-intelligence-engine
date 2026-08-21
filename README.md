# Price Intelligence Engine & Web Scraping Foundations

This repository contains lessons, notes, and working scripts covering the foundations of web scraping and price intelligence in Python.

---

## Day 02 — Implement Basic HTTP Request
*See [`http_scraping_foundations.py`](./http_scraping_foundations.py)*

- **GET Requests:** Requesting data using `requests.get(url, headers=headers)`.
- **Status Codes:** Understanding `200 OK`, `403 Forbidden`, `404 Not Found`, and `500 Server Error`.
- **User-Agents:** Setting custom headers to emulate standard desktop web browsers.
- **`.text` vs `.content`:** Using `.text` for strings/HTML, and `.content` for raw bytes (images/PDFs).

---

## Day 3 — HTML Structure
*See [`day_03_html_structure.py`](./day_03_html_structure.py)*

### Learn

#### Understand HTML Hierarchy:

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

* **`<html>`**: The root element wrapping the entire webpage.
* **`<head>`**: Contains metadata, page title, and stylesheet links (non-visible).
* **`<body>`**: Encloses all visible content on the webpage.
* **`<div>`**: Container element used to group structural components (e.g., product cards).
* **`<span>`**: Inline container used for styling or holding short text fragments.
* **`<a>`**: Anchor tag defining hyperlinks (`href` attribute).
* **`<img>`**: Image tag referencing media files (`src` attribute).

---

### Practice Identifying Target Data

On an e-commerce page (e.g., [books.toscrape.com](http://books.toscrape.com/)), target elements are mapped as:

1. **Product Title**: Stored in inner text or `title` attribute of `<a>` inside `<h3>`.
2. **Price**: Stored in inner text of `<p class="price_color">`.
3. **Product URL**: Stored in the `href` attribute of the `<a>` link tag.
4. **Image URL**: Stored in the `src` attribute of the `<img>` image tag.

---

### Build & Run Practice Scripts

```bash
# Install dependencies
pip install requests beautifulsoup4

# Run Day 02 (HTTP Requests)
python http_scraping_foundations.py

# Run Day 03 (HTML Structure & BeautifulSoup Parsing)
python day_03_html_structure.py
```
