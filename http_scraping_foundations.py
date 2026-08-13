"""
HTTP Requests Foundations for Web Scraping in Python
===================================================

This script demonstrates the core HTTP request concepts needed for web scraping:
- Custom HTTP headers (User-Agent)
- Making GET requests with requests library
- Status code handling and exception management
- Accessing response HTML text (.text vs .content)
"""

import sys
import requests

# Ensure stdout handles UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def fetch_page_html(target_url: str) -> str | None:
    """
    Fetches the HTML content of a URL with browser headers and status checking.

    Args:
        target_url (str): The URL of the web page to request.

    Returns:
        str | None: Raw HTML text string if successful, None if an error occurred.
    """
    # 1. Custom Headers (Disguise request to look like a desktop browser)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        print(f"Sending GET request to {target_url}...")

        # 2. GET Request with custom headers & timeout
        response = requests.get(target_url, headers=headers, timeout=10)

        # 3. Status Code Handling (raises exception for 4xx or 5xx codes)
        response.raise_for_status()

        print(f"[SUCCESS] Status Code: {response.status_code}")

        # 4. Access HTML content as string (.text)
        return response.text

    except requests.exceptions.HTTPError as http_err:
        print(f"[ERROR] HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Failed to connect to server. Check your connection/URL.")
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out after 10 seconds.")
    except requests.exceptions.RequestException as err:
        print(f"[ERROR] An unexpected error occurred: {err}")

    return None


if __name__ == "__main__":
    test_url = "https://example.com"
    html_content = fetch_page_html(test_url)

    if html_content:
        print("\n--- Preview of HTML Payload (.text) ---")
        print(html_content[:300])  # Display first 300 characters
