"""
BookMyShow MI vs RCB Ticket Availability Checker
Checks if tickets are available and sends a Discord alert.
"""

import os
import sys
from datetime import datetime

import cloudscraper
import requests
from bs4 import BeautifulSoup

_scraper = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "darwin", "mobile": False})

# ── CONFIG ────────────────────────────────────────────────────────────────────

# The BMS event URL for MI vs RCB (April 12, 2026)
BMS_EVENT_URL = "https://in.bookmyshow.com/sports/mumbai-indians-vs-royal-challengers-bengaluru/ET00491196?data=groupPage"

# Strings in the BMS page that indicate tickets ARE available
AVAILABILITY_SIGNALS = [
    "Book Now",
    "book now",
    "BOOK NOW",
    "BuyNow",
    "buy-now",
    "bookButton",
    "Select Seats",
    "select-seats",
    "Fast Filling",
    "fast filling",
    "Filling Fast",
    "filling fast",
    "Going Fast",
    "going fast",
    "Few Tickets",
    "few tickets",
    "Limited Tickets",
    "limited tickets",
    "Available",
]

# Strings that mean tickets are NOT yet available
UNAVAILABLE_SIGNALS = [
    "Sold Out",
    "sold-out",
    "Coming Soon",
    "Notify Me",
    "Registration Closed",
]

# Discord webhook URL — set this as a GitHub Secret
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

# ── HEADERS (mimic a real browser to avoid bot blocks) ────────────────────────

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

# ── CORE LOGIC ────────────────────────────────────────────────────────────────

def fetch_page(url: str) -> str | None:
    """Fetch a URL and return HTML, or None on failure."""
    try:
        resp = _scraper.get(url, headers=HEADERS, timeout=15)
        print(f"  → GET {url}  [status {resp.status_code}]")
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        print(f"  ✗ Request failed: {e}")
        return None


def check_availability(html: str) -> tuple[bool, str]:
    """
    Return (is_available, reason_string) by scanning page HTML.
    """
    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text(" ", strip=True)
    raw_html = html

    # First check unavailability signals
    for signal in UNAVAILABLE_SIGNALS:
        if signal.lower() in page_text.lower():
            return False, f"Unavailability signal found: '{signal}'"

    # Then check for positive booking signals
    for signal in AVAILABILITY_SIGNALS:
        if signal.lower() in page_text.lower() or signal in raw_html:
            return True, f"Availability signal found: '{signal}'"

    return False, "No booking signal detected on page"


def send_discord(content: str, embeds: list | None = None):
    """Post a message to the Discord webhook."""
    payload = {"content": content}
    if embeds:
        payload["embeds"] = embeds

    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        resp.raise_for_status()
        print("  ✉️  Discord notification sent.")
    except Exception as e:
        print(f"  ✗ Failed to send Discord notification: {e}")
        sys.exit(1)


def send_ticket_alert(url: str, reason: str):
    """Send a Discord alert that tickets are available."""
    now = datetime.now().strftime("%d %b %Y, %I:%M %p IST")
    send_discord(
        content="@everyone",
        embeds=[{
            "title": "🚨 MI vs RCB Tickets AVAILABLE on BookMyShow!",
            "color": 0xFF0000,
            "fields": [
                {"name": "Match", "value": "Mumbai Indians vs Royal Challengers Bengaluru", "inline": False},
                {"name": "Venue", "value": "Wankhede Stadium, Mumbai", "inline": True},
                {"name": "Date", "value": "April 12, 2026 — 7:30 PM IST", "inline": True},
                {"name": "Detection", "value": reason, "inline": False},
                {"name": "Checked at", "value": now, "inline": False},
            ],
            "description": f"[👉 Book Now on BookMyShow]({url})",
        }],
    )


def send_heartbeat(available: bool, reason: str):
    """Send a heartbeat notification every run so you know the bot is alive."""
    now = datetime.now().strftime("%d %b %Y, %I:%M %p IST")
    if available:
        # This case is handled by send_ticket_alert, skip heartbeat
        return
    send_discord(
        embeds=[{
            "title": "🤖 BMS Checker: Still watching",
            "color": 0x5865F2,
            "fields": [
                {"name": "Status", "value": f"No tickets yet — {reason}", "inline": False},
                {"name": "Checked at", "value": now, "inline": False},
            ],
        }]
    )


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*55}")
    print(f"  BMS Ticket Checker  |  {datetime.now().strftime('%d %b %Y %H:%M:%S')}")
    print(f"{'='*55}")

    url = BMS_EVENT_URL
    print(f"\nChecking: {url}")
    html = fetch_page(url)

    if not html:
        print("  → Could not fetch page.")
        send_discord("⚠️ BMS Checker: Failed to fetch the event page. Check the URL or if BMS is blocking requests.")
        sys.exit(1)

    available, reason = check_availability(html)
    print(f"  → Available: {available} | {reason}")

    if available:
        print("\n  🎉 TICKETS FOUND! Sending alert...")
        send_ticket_alert(url, reason)
        with open("TICKET_FOUND.txt", "w") as f:
            f.write(f"Tickets found at {url}\nReason: {reason}\n")
        sys.exit(0)

    # Always send heartbeat so you know the script ran
    send_heartbeat(available, reason)
    print("\n  😴 No tickets available yet. Heartbeat sent.")
    sys.exit(0)


if __name__ == "__main__":
    main()
