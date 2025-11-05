# tools/utils.py
import json
from pathlib import Path
import time

# Path to your cookies JSON
COOKIE_FILE = Path(r"C:\Users\mayank manjhi\Downloads\(1)lang,rag,ai\profiles\uc_x_cookies.json")

def apply_saved_cookies(driver):
    """Load cookies from JSON into Selenium driver (synchronous)."""
    if not COOKIE_FILE.exists():
        raise FileNotFoundError(f"Cookies file not found: {COOKIE_FILE}")
    
    cookies = json.load(COOKIE_FILE.open())
    
    # Open X.com to set domain
    driver.get("https://x.com")
    time.sleep(2)
    
    for c in cookies:
        # Selenium expects expires as int or omitted
        if "expires" in c and isinstance(c["expires"], str):
            c.pop("expires", None)
        # Fix domain format for Selenium
        if "domain" in c and c["domain"].startswith("."):
            c["domain"] = c["domain"].lstrip(".")
        try:
            driver.add_cookie(c)
        except Exception:
            # skip invalid cookies
            pass
    print("✅ Cookies loaded into Selenium driver.")
