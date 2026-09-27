"""
Day 19 — Anti-Bot Evasion & Request Fingerprinting
==================================================
Learn & Practice techniques to bypass bot detection systems:
- TLS/JA3 fingerprinting awareness and browser headers consistency
- Simulating human request behavior (jitter delays, referrer headers, cookie management)
- Defensively inspecting response challenges (Cloudflare, Akamai)
"""

import random
import sys
import time
from typing import Any, Dict
import requests

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def generate_browser_fingerprint() -> Dict[str, str]:
    """Generates a consistent set of browser headers (sec-ch-ua, accept, platform)."""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
    }


def human_like_request(url: str, session: requests.Session | None = None) -> str | None:
    """Performs HTTP request with simulated human delay jitter and full header fingerprint."""
    if session is None:
        session = requests.Session()

    # Apply random human delay (1.2 to 2.5 seconds jitter)
    jitter_delay = round(random.uniform(1.2, 2.5), 2)
    print(f"⏳ Human simulation delay: Pausing {jitter_delay}s before requesting {url}...")
    time.sleep(jitter_delay)

    headers = generate_browser_fingerprint()
    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Check for bot challenge keywords
        if "cf-challenge" in response.text.lower() or "just a moment" in response.text.lower():
            print("⚠️ Cloudflare bot challenge detected in response payload!")
        else:
            print("✅ Request passed anti-bot fingerprint checks.")

        return response.text
    except Exception as err:
        print(f"❌ Request failed: {err}")
        return None


def run_day_19_demo():
    url = "http://books.toscrape.com/"
    print("[Day 19] Running Anti-Bot Evasion & Fingerprinting Module...\n")
    session = requests.Session()
    human_like_request(url, session)


if __name__ == "__main__":
    run_day_19_demo()
