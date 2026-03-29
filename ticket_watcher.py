"""
Ticket Watcher — Indian Proxy Version
Routes through Indian proxy so BookMyShow serves the real page
"""

import os
import time
import requests
from datetime import datetime

PAGE_URL             = os.environ.get("PAGE_URL", "")
KEYWORDS             = os.environ.get("KEYWORDS", "Filling Fast,filling fast,Book Now").split(",")
CHECK_EVERY_SECONDS  = int(os.environ.get("CHECK_EVERY_SECONDS", "30"))
TWILIO_ACCOUNT_SID   = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN    = os.environ.get("TWILIO_AUTH_TOKEN", "")
YOUR_WHATSAPP_NUMBER = os.environ.get("YOUR_WHATSAPP_NUMBER", "")
TWILIO_FROM          = "whatsapp:+14155238886"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://in.bookmyshow.com/",
    "X-Forwarded-For": "103.21.58.100",
}

def log(msg, symbol="•"):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] {symbol} {msg}", flush=True)

def send_whatsapp(message):
    try:
        from twilio.rest import Client
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
    try:
        # Try direct first
        response = requests.get(PAGE_URL, headers=HEADERS, timeout=15)
        page_text = response.text.lower()
        log(f"Page size: {len(page_text)} chars | Status: {response.status_code}")

        found = [kw.strip() for kw in KEYWORDS if kw.strip().lower() in page_text]

        # Log a snippet to see what we're getting
        if "filling" in page_text:
            log("'filling' found in page ✅")
        elif "bookmyshow" in page_text:
            log("BMS page loaded but no keywords yet")
        else:
            log("Page may be blocked or redirected")

        return found
    except Exception as e:
        log(f"Error: {e}", "⚠️")
        return []

def main():
    print("=" * 50, flush=True)
    print("  TICKET WATCHER (Indian Headers Mode)", flush=True)
    print("=" * 50, flush=True)
    log(f"Watching: {PAGE_URL}")
    log(f"Keywords: {', '.join(KEYWORDS)}")
    log(f"Checking every {CHECK_EVERY_SECONDS} seconds")
    print("=" * 50, flush=True)

    check_count = 0
    while True:
        check_count += 1
        log(f"Check #{check_count}...")
        found = check_page()
        if found:
            log(f"TICKETS FOUND! Keywords: {', '.join(found)}", "🎟️")
            msg = f"🎟 TICKETS LIVE!\n\nFound: {', '.join(found)}\n\nBook now → {PAGE_URL}"
            send_whatsapp(msg)
            log("Alert sent! Checking again in 5 mins...")
            time.sleep(300)
        else:
            log(f"Not live yet. Next check in {CHECK_EVERY_SECONDS}s...")
            time.sleep(CHECK_EVERY_SECONDS)

if __name__ == "__main__":
    main()
