# utils.py

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Optional cookie file path
ACTION_COOKIE_FILE = "cookies/action_cookies.json"

def start_driver(headless=False, use_profile=True, profile_dir="Default"):
    """
    Starts a single stable Chrome browser instance.
    - Uses your existing Chrome profile if use_profile=True
    - Avoids double opening or crash
    """
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--start-maximized")

    if headless:
        chrome_options.add_argument("--headless=new")

    if use_profile:
        user_data_dir = r"C:\Users\mayank manjhi\AppData\Local\Google\Chrome\User Data"
        if not os.path.exists(user_data_dir):
            raise FileNotFoundError("Chrome user data directory not found! Check path.")
        chrome_options.add_argument(f"user-data-dir={user_data_dir}")
        chrome_options.add_argument(f"profile-directory={profile_dir}")

    # ✅ Single Chrome launch (no duplication)
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(60)

    # Wait to stabilize browser
    time.sleep(2)
    return driver
