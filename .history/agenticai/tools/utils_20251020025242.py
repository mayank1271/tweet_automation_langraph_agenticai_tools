# agenticai/tools/utils.py
import json, time, os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import os

# Paths (edit to your environment)
COOKIE_FILE = Path(r"C:\Users\mayank manjhi\Downloads\(1)lang,rag,ai\profiles\uc_x_cookies.json")  # original
ACTION_COOKIE_FILE = Path(r"C:\Users\mayank manjhi\Downloads\(1)lang,rag,ai\agenticai\tools\action_cookies.json")

# Default Chrome user-data dir (example). Change to your path if you want profile mode.
DEFAULT_USER_DATA_DIR = r"C:\Users\mayank manjhi\AppData\Local\Google\Chrome\User Data"
DEFAULT_PROFILE = "Default"  # or "Profile 1"


def start_driver(headless=False, use_profile=True, profile_dir="Default"):
    options = webdriver.ChromeOptions()
    
    # ✅ Disable automation warnings
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")

    if headless:
        options.add_argument("--headless=new")

    if use_profile:
        user_data_dir = r"C:\Users\mayank manjhi\AppData\Local\Google\Chrome\User Data"
        options.add_argument(f"user-data-dir={user_data_dir}")
        options.add_argument(f"profile-directory={profile_dir}")

    # ✅ Add this to avoid Chrome crash in profile mode
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Path to ChromeDriver (if not in PATH)
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(60)
    return driver


def save_cookies(driver, path=ACTION_COOKIE_FILE):
    cookies = driver.get_cookies()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=2)
    print("✅ Cookies saved to", path)

def apply_saved_cookies(driver, path=ACTION_COOKIE_FILE):
    if not Path(path).exists():
        raise FileNotFoundError(f"Cookies file not found: {path}")
    cookies = json.load(open(path, "r", encoding="utf-8"))
    driver.get("https://x.com")
    time.sleep(2)
    for c in cookies:
        # remove string expires and fix domain leading dot
        if "expires" in c and isinstance(c["expires"], str):
            c.pop("expires", None)
        if "domain" in c and isinstance(c["domain"], str) and c["domain"].startswith("."):
            c["domain"] = c["domain"].lstrip(".")
        try:
            driver.add_cookie(c)
        except Exception:
            pass
    print("✅ Cookies loaded into Selenium driver (from JSON).")

def manual_login_and_save(use_profile=False, user_data_dir=None, profile_dir=None, headless=False):
    """
    Opens a browser for manual login and saves cookies to ACTION_COOKIE_FILE.
    If use_profile=True it will open the profile, otherwise a fresh profile.
    """
    driver = start_driver(headless=headless, use_profile=use_profile, user_data_dir=user_data_dir, profile_dir=profile_dir)
    driver.get("https://x.com/login")
    input("➡️ Please log in manually in the opened browser, then press ENTER here...")
    save_cookies(driver)
    driver.quit()
    print("✅ Manual login done and cookies saved for automated actions.")
