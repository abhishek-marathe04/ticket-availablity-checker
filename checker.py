"""
BookMyShow MI vs RCB Ticket Availability Checker
Checks if tickets are available and sends a Gmail alert.
"""

import os
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from bs4 import BeautifulSoup

# ── CONFIG ────────────────────────────────────────────────────────────────────

# The BMS event URL for MI vs RCB at Wankhede (April 12, 2026)
# This is the direct search/event URL — update if BMS changes it
BMS_EVENT_URL = "https://in.bookmyshow.com/sports/mumbai-indians-vs-royal-challengers-bengaluru/ET00408726"

# Fallback: BMS search page for IPL in Mumbai
BMS_SEARCH_URL = "https://in.bookmyshow.com/explore/sports/mumbai"

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
]

# Strings that mean tickets are NOT yet available (sold out / coming soon)
UNAVAILABLE_SIGNALS = [
    "Sold Out",
    "sold-out",
    "Coming Soon",
    "Notify Me",
    "Registration Closed",
]

# Gmail credentials — set these as GitHub Secrets
GMAIL_USER = os.environ["GMAIL_USER"]          # your Gmail address
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]   # Gmail App Password
ALERT_TO_EMAIL = os.environ.get("ALERT_TO_EMAIL", GMAIL_USER)  # who to notify

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
        resp = requests.get(url, headers=HEADERS, timeout=15)
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
    raw_html = html  # also search raw HTML for class/id signals

    # First check unavailability signals (they appear even when a page exists)
    for signal in UNAVAILABLE_SIGNALS:
        if signal.lower() in page_text.lower():
            return False, f"Unavailability signal found: '{signal}'"

    # Then check for positive booking signals
    for signal in AVAILABILITY_SIGNALS:
        if signal.lower() in page_text.lower() or signal in raw_html:
            return True, f"Availability signal found: '{signal}'"

    return False, "No booking signal detected on page"


def send_email_alert(url: str, reason: str):
    """Send a Gmail notification that tickets are available."""
    now = datetime.now().strftime("%d %b %Y, %I:%M %p IST")

    subject = "🚨 MI vs RCB Tickets AVAILABLE on BookMyShow!"

    html_body = f"""
    <html><body style="font-family: Arial, sans-serif; line-height: 1.6;">
      <h2 style="color: #1a73e8;">🏏 Ticket Alert: MI vs RCB</h2>
      <p><strong>Match:</strong> Mumbai Indians vs Royal Challengers Bengaluru</p>
      <p><strong>Venue:</strong> Wankhede Stadium, Mumbai</p>
      <p><strong>Date:</strong> April 12, 2026 — 7:30 PM IST</p>
      <hr/>
      <p>✅ <strong>Tickets appear to be available!</strong></p>
      <p><em>Detection reason:</em> {reason}</p>
      <p><em>Checked at:</em> {now}</p>
      <hr/>
      <p>
        <a href="{url}" style="
          background: #1a73e8; color: white; padding: 10px 20px;
          text-decoration: none; border-radius: 5px; font-weight: bold;
        ">👉 Book Now on BookMyShow</a>
      </p>
      <p style="color: #888; font-size: 12px;">
        This is an automated alert. Availability may change quickly — book fast!
      </p>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = ALERT_TO_EMAIL
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, ALERT_TO_EMAIL, msg.as_string())
        print(f"  ✉️  Alert email sent to {ALERT_TO_EMAIL}")
    except Exception as e:
        print(f"  ✗ Failed to send email: {e}")
        sys.exit(1)


def send_heartbeat_email():
    """
    Optional: send a daily 'still watching' email so you know the bot is alive.
    Only runs if the env var SEND_HEARTBEAT=true.
    """
    if os.environ.get("SEND_HEARTBEAT", "").lower() != "true":
        return

    now = datetime.now().strftime("%d %b %Y, %I:%M %p")
    subject = "🤖 BMS Checker: Still watching (no tickets yet)"
    body = f"The MI vs RCB ticket checker ran at {now}. No tickets found yet. Will keep watching."

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = ALERT_TO_EMAIL
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, ALERT_TO_EMAIL, msg.as_string())
        print("  💌 Heartbeat email sent.")
    except Exception as e:
        print(f"  ✗ Heartbeat email failed: {e}")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*55}")
    print(f"  BMS Ticket Checker  |  {datetime.now().strftime('%d %b %Y %H:%M:%S')}")
    print(f"{'='*55}")

    urls_to_check = [BMS_EVENT_URL, BMS_SEARCH_URL]

    for url in urls_to_check:
        print(f"\nChecking: {url}")
        html = fetch_page(url)

        if not html:
            print("  → Could not fetch page, skipping.")
            continue

        available, reason = check_availability(html)
        print(f"  → Available: {available} | {reason}")

        if available:
            print("\n  🎉 TICKETS FOUND! Sending alert...")
            send_email_alert(url, reason)
            # Write a flag file so the GH Actions summary shows it
            with open("TICKET_FOUND.txt", "w") as f:
                f.write(f"Tickets found at {url}\nReason: {reason}\n")
            sys.exit(0)  # success, alert sent

    # No tickets found on any URL
    print("\n  😴 No tickets available yet. Will check again next run.")
    send_heartbeat_email()
    sys.exit(0)


if __name__ == "__main__":
    main()
