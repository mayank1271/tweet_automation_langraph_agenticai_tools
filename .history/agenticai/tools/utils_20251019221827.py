# tools/utils.py (updated)
import json
from pathlib import Path
import time

COOKIE_FILE = Path(r"C:\Users\mayank manjhi\Downloads\(1)lang,rag,ai\profiles\uc_x_cookies.json")

def apply_saved_cookies(driver):
    """Load cookies from JSON into Selenium driver and refresh page."""
    if not COOKIE_FILE.exists():
        raise FileNotFoundError(f"Cookies file not found: {COOKIE_FILE}")
    
    cookies = json.load(COOKIE_FILE.open())
    
    # Open base page
    driver.get("https://x.com")
    time.sleep(3)
    
    for c in cookies:
        # Fix domain format
        if "domain" in c and c["domain"].startswith("."):
            c["domain"] = c["domain"].lstrip(".")
        # Remove expires if string
        if "expires" in c and isinstance(c["expires"], str):
            c.pop("expires", None)
        # Set default flags if missing
        if "secure" not in c:
            c["secure"] = True
        if "httpOnly" not in c:
            c["httpOnly"] = False
        try:
            driver.add_cookie(c)
        except Exception as ex:
            print(f"⚠️ Skipped cookie: {c.get('name')} ({ex})")
    
    # Refresh page to apply cookies
    driver.refresh()
    time.sleep(5)
    
    # Verify login by checking home page element
    driver.get("https://x.com/home")
    time.sleep(5)
    if "login" in driver.current_url.lower():
        print("❌ Not logged in — cookies may be invalid or expired.")
    else:
        print("✅ Cookies applied and logged in successfully!")
