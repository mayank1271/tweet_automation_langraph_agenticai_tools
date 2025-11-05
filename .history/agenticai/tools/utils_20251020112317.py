import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def start_driver(headless=False, use_profile=True, profile_dir="Default"):
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")

    if headless:
        chrome_options.add_argument("--headless=new")

    if use_profile:
        # 👇 This is your verified local profile path
        chrome_options.add_argument(r"--user-data-dir=C:\Users\mayank manjhi\AppData\Local\Google\Chrome\User Data")
        chrome_options.add_argument(r"--profile-directory=Default")
    else:
        chrome_options.add_argument("--guest")

    driver = webdriver.Chrome(service=Service(), options=chrome_options)
    time.sleep(2)
    return driver
