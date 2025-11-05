# utils.py
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

ACTION_COOKIE_FILE = "cookies/action_cookies.json"

def start_driver(headless=False, use_profile=True, profile_dir="Default"):
    chrome_options = Options()

    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--start-maximized")

    if headless:
        chrome_options.add_argument("--headless=new")

    if use_profile:
        # 👇 Your local Chrome profile path
        user_data_dir = r"C:\Users\mayank manjhi\AppData\Local\Google\Chrome\User Data"
        chrome_options.add_argument(f"user-data-dir={user_data_dir}")
        chrome_options.add_argument(f"profile-directory={profile_dir}")

        # ⚠️ critical fix: separate temp dir to avoid profile locking
        temp_dir = os.path.join(os.getcwd(), "chrome_temp")
        os.makedirs(temp_dir, exist_ok=True)
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")

    service = Service()  # auto-detect chromedriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(60)

    time.sleep(2)
    return driver
