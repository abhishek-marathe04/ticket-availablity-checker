"""
Quick test for BookMyShow scraping — no email credentials needed.
Run: python test_bms.py
"""

import sys
import requests
from bs4 import BeautifulSoup

BMS_EVENT_URL = "https://in.bookmyshow.com/sports/mumbai-indians-vs-royal-challengers-bengaluru/ET00491196?data=groupPage"
BMS_SEARCH_URL = "https://in.bookmyshow.com/explore/sports/mumbai"

AVAILABILITY_SIGNALS = [
    "Book Now", "book now", "BOOK NOW",
    "BuyNow", "buy-now", "bookButton",
    "Select Seats", "select-seats",
    "Fast Filling", "fast filling",
    "Filling Fast", "filling fast",
    "Going Fast", "going fast",
    "Few Tickets", "few tickets",
    "Limited Tickets", "limited tickets",
    "Available",
]

UNAVAILABLE_SIGNALS = [
    "Sold Out", "sold-out", "Coming Soon",
    "Notify Me", "Registration Closed",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://in.bookmyshow.com/",
}


def fetch_page(url: str) -> str | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        print(f"  HTTP {resp.status_code}  ({len(resp.text):,} chars received)")
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        print(f"  ERROR: {e}")
        return None


def check_availability(html: str) -> tuple[bool, str]:
    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text(" ", strip=True)

    for signal in UNAVAILABLE_SIGNALS:
        if signal.lower() in page_text.lower():
            return False, f"Unavailability signal: '{signal}'"

    for signal in AVAILABILITY_SIGNALS:
        if signal.lower() in page_text.lower() or signal in html:
            return True, f"Availability signal: '{signal}'"

    return False, "No booking signal detected"


def dump_page_snippet(html: str, chars: int = 2000):
    """Print a snippet of the visible text so you can sanity-check what BMS returned."""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    print(f"\n--- Page text snippet (first {chars} chars) ---")
    print(text[:chars])
    print("--- end snippet ---")


def main():
    urls = [
        ("Event page", BMS_EVENT_URL)
    ]

    for label, url in urls:
        print(f"\n{'='*60}")
        print(f"  {label}")
        print(f"  {url}")
        print(f"{'='*60}")

        html = fetch_page(url)
        if not html:
            print("  Could not fetch page — skipping.")
            continue

        available, reason = check_availability(html)
        status = "AVAILABLE ✅" if available else "NOT available ❌"
        print(f"\n  Result  : {status}")
        print(f"  Reason  : {reason}")

        dump_page_snippet(html)

    print(f"\n{'='*60}")
    print("  Done. Check the output above to verify BMS is returning")
    print("  the right page and the signals look correct.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
