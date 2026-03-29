"""
Ticket Watcher — Button Click Detection Version
Uses Selenium to actually open the page in a real browser and try clicking Book Now.
If the button is clickable = tickets are live!
"""

import os
import time
from datetime import datetime

PAGE_URL             = os.environ.get("PAGE_URL", "")
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

def check_button():
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.get(PAGE_URL)

        # Wait up to 8 seconds for page to load
        wait = WebDriverWait(driver, 8)

        # Look for Book Now button
        try:
            btn = wait.until(
                EC.presence_of_element_located((By.XPATH,
                    "//a[contains(text(),'Book Now')] | "
                    "//button[contains(text(),'Book Now')] | "
                    "//a[contains(@class,'book')] | "
                    "//button[contains(@class,'book')]"
                ))
            )

            # Check if button is enabled and visible
            if btn.is_displayed() and btn.is_enabled():
                # Check it's not greyed out
                classes = btn.get_attribute("class") or ""
                style = btn.get_attribute("style") or ""
                aria = btn.get_attribute("aria-disabled") or "false"

                if "disabled" not in classes.lower() and aria != "true":
                    log(f"Book Now button found and ACTIVE!", "🎟️")
                    return True
                else:
                    log("Book Now button found but disabled/greyed out.")
                    return False
            else:
                log("Book Now button not visible.")
                return False

        except Exception:
            log("Book Now button not found on page.")
            return False

    except Exception as e:
        log(f"Browser error: {e}", "⚠️")
        return False
    finally:
        if driver:
            driver.quit()

def main():
    print("=" * 50, flush=True)
    print("  TICKET WATCHER (Button Click Mode)", flush=True)
    print("=" * 50, flush=True)
    log(f"Watching: {PAGE_URL}")
    log(f"Method: Looking for active Book Now button")
    log(f"Checking every {CHECK_EVERY_SECONDS} seconds")
    print("=" * 50, flush=True)

    check_count = 0

    while True:
        check_count += 1
        log(f"Check #{check_count}...")

        tickets_live = check_button()

        if tickets_live:
            log("TICKETS ARE LIVE!", "🎟️")
            msg = (
                f"🎟 TICKETS ARE LIVE!\n\n"
                f"Book Now button is active!\n\n"
                f"Book now → {PAGE_URL}"
            )
            send_whatsapp(msg)
            log("Alert sent! Will check again in 5 mins...")
            time.sleep(300)
        else:
            log(f"Not live yet. Next check in {CHECK_EVERY_SECONDS}s...")
            time.sleep(CHECK_EVERY_SECONDS)

if __name__ == "__main__":
    main()
