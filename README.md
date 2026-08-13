# HTTP Requests for Web Scraping in Python

A foundational guide to understanding and making HTTP requests for web scraping in Python using the `requests` library.

---

## 1. HTTP Basics: Sending a Request

### 🍔 The Restaurant Analogy
* **Client (Python Script):** You place an order with the waiter (**HTTP Request**).
* **Server (Website Kitchen):** Receives your request, processes it, and prepares the web page.
* **Response (Meal & Receipt):** The server returns the payload (HTML/data) along with metadata (**Status Code** & **Headers**).

---

## 2. GET Requests in Python

A **GET request** fetches data from a server without modifying anything on the remote site.

```bash
pip install requests
```

```python
import requests

response = requests.get("https://example.com")
```

---

## 3. HTTP Status Codes

Status codes are 3-digit numbers returned by the server indicating the result of the request:

| Code | Meaning | Scraping Context |
| :--- | :--- | :--- |
| **`200 OK`** | Success | Request succeeded; payload ready for scraping. |
| **`403 Forbidden`** | Access Denied | Server detected bot traffic or blocked your IP/User-Agent. |
| **`404 Not Found`** | Page Missing | Invalid URL or page no longer exists. |
| **`500 Internal Error`** | Server Error | Website crashed internally. |

```python
# Automatic status checking
response.raise_for_status()
```

---

## 4. Headers & User-Agents

Websites check request headers to filter out automated scripts. Default `requests` headers broadcast `User-Agent: python-requests/...`, which frequently leads to **403 Forbidden** errors.

To avoid unnecessary blocks, pass custom desktop browser headers:

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

response = requests.get("https://example.com", headers=headers)
```

---

## 5. HTML Response: `.text` vs `.content`

- **`response.text`**: Returns HTML/text decoded as a `str` (95% of scraping tasks).
- **`response.content`**: Returns raw binary bytes (`bytes`). Use this for downloading images, PDFs, or files.

---

## 6. Complete Python Example

Run [`http_scraping_foundations.py`](./http_scraping_foundations.py) to test out these concepts.
