"""
Ticket Watcher — Railway Cloud Version
Reads all config from environment variables set in Railway dashboard.
"""

import os
import time
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
from datetime import datetime

# Read from Railway environment variables
PAGE_URL             = os.environ.get("PAGE_URL", "")
KEYWORDS             = os.environ.get("KEYWORDS", "Book Now,Buy Tickets,Available,Book").split(",")
CHECK_EVERY_SECONDS  = int(os.environ.get("CHECK_EVERY_SECONDS", "30"))
TWILIO_ACCOUNT_SID   = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN    = os.environ.get("TWILIO_AUTH_TOKEN", "")
YOUR_WHATSAPP_NUMBER = os.environ.get("YOUR_WHATSAPP_NUMBER", "")
TWILIO_FROM          = "whatsapp:+14155238886"

def log(msg, symbol="•"):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] {symbol} {msg}", flush=True)

def send_whatsapp(message):
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=TWILIO_FROM,
            to=f"whatsapp:{YOUR_WHATSAPP_NUMBER}"
        )
        log("WhatsApp message sent!", "✅")
    except Exception as e:
        log(f"WhatsApp send failed: {e}", "❌")

def check_page():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        response = requests.get(PAGE_URL, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        page_text = soup.get_text().lower()
        found = [kw.strip() for kw in KEYWORDS if kw.strip().lower() in page_text]
        return found
    except Exception as e:
        log(f"Error fetching page: {e}", "⚠️")
        return []

def main():
    print("=" * 50, flush=True)
    print("  TICKET WATCHER STARTED (Railway Cloud)", flush=True)
    print("=" * 50, flush=True)
    log(f"Watching: {PAGE_URL}")
    log(f"Keywords: {', '.join(KEYWORDS)}")
    log(f"Checking every {CHECK_EVERY_SECONDS} seconds")
    log(f"WhatsApp alerts → {YOUR_WHATSAPP_NUMBER}")
    print("=" * 50, flush=True)

    check_count = 0

    while True:
        check_count += 1
        log(f"Check #{check_count}...")
        found = check_page()
        if found:
            log(f"TICKETS FOUND! Keywords: {', '.join(found)}", "🎟️")
            msg = (
                f"🎟 TICKETS AVAILABLE!\n\n"
                f"Found: {', '.join(found)}\n\n"
                f"Book now → {PAGE_URL}"
            )
            send_whatsapp(msg)
            log("Alert sent! Watching for more...")
            time.sleep(CHECK_EVERY_SECONDS * 10)
        else:
            log(f"Not available yet. Next check in {CHECK_EVERY_SECONDS}s...")
            time.sleep(CHECK_EVERY_SECONDS)

if __name__ == "__main__":
    main()
