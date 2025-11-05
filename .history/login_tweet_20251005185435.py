# cookie_extractor.py
from playwright.sync_api import sync_playwright
import json

COOKIE_PATH = r"C:\Users\mayank manjhi\Downloads\(1)lang,rag,ai\x_cookies.json"

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir="C:/Users/mayank manjhi/AppData/Local/Google/Chrome/User Data",
        headless=False,
    )
    page = browser.new_page()
    page.goto("https://x.com/home")
    input("Login manually in Chrome window if needed, then press Enter...")
    cookies = browser.cookies()
    with open(COOKIE_PATH, "w") as f:
        json.dump(cookies, f, indent=2)
    print("✅ Cookies saved to", COOKIE_PATH)
    browser.close()
