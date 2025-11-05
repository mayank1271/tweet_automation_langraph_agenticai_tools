# tools/utils.py
import json
from pathlib import Path
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

# ------------------------------
# Cookie files
# ------------------------------
# Original cookies (may expire, backup)
COOKIE_FILE = Path(r"C:\Users\mayank manjhi\Downloads\(1)lang,rag,ai\profiles\uc_x_cookies.json")

# Cookies used for automated actions
ACTION_COOKIE_FILE = Path(r"C:\Users\mayank manjhi\Downloads\(1)lang,rag,ai\agenticai\tools\action_cookies.json")

# ------------------------------
# Selenium Driver Helper
# ------------------------------
def start_driver(headless=True):
    """Start undetected Chrome driver."""
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    return driver

# ------------------------------
# Cookies Handling
# ------------------------------
def save_cookies(driver, path=ACTION_COOKIE_FILE):
    """Save cookies from current Selenium session."""
    cookies = driver.get_cookies()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=4)
    print(f"✅ Cookies saved to: {path}")

def apply_saved_cookies(driver, path=ACTION_COOKIE_FILE):
    """Load cookies from JSON into Selenium driver."""
    if not path.exists():
        raise FileNotFoundError(f"Cookies file not found: {path}")
    
    cookies = json.load(path.open())
    driver.get("https://x.com")
    time.sleep(2)
    
    for c in cookies:
        # Selenium expects expires as int or omitted
        if "expires" in c and isinstance(c["expires"], str):
            c.pop("expires", None)
        if "domain" in c and c["domain"].startswith("."):
            c["domain"] = c["domain"].lstrip(".")
        try:
            driver.add_cookie(c)
        except Exception:
            pass
    print("✅ Cookies loaded into Selenium driver.")

# ------------------------------
# Automated Actions
# ------------------------------
def like_tweet(tweet_url, headless=True):
    driver = start_driver(headless)
    try:
        apply_saved_cookies(driver)
        driver.refresh()
        time.sleep(5)
        driver.get(tweet_url)
        time.sleep(5)

        print("🔍 Searching for Like button...")
        like_btns = driver.find_elements(By.XPATH, "//button[@data-testid='like']")
        for btn in like_btns:
            try:
                ActionChains(driver).move_to_element(btn).pause(0.5).click().perform()
                print(f"❤️ Successfully liked tweet: {tweet_url}")
                return True
            except Exception:
                continue
        print("❌ No clickable Like button found.")
        return False
    finally:
        driver.quit()

def repost_tweet(tweet_url, headless=True):
    driver = start_driver(headless)
    try:
        apply_saved_cookies(driver)
        driver.refresh()
        time.sleep(5)
        driver.get(tweet_url)
        time.sleep(5)

        print("🔍 Searching for Repost button...")
        repost_btns = driver.find_elements(By.XPATH, "//button[@data-testid='retweet']")
        for btn in repost_btns:
            try:
                ActionChains(driver).move_to_element(btn).pause(0.5).click().perform()
                time.sleep(2)
                menu_options = driver.find_elements(By.XPATH, "//span[text()='Repost']")
                if menu_options:
                    menu_options[0].click()
                    print(f"🔁 Successfully reposted: {tweet_url}")
                    return True
                else:
                    print("⚠️ Repost menu not found — maybe already reposted or slow load.")
                    return False
            except Exception:
                continue
        print("❌ No clickable Repost button found.")
        return False
    finally:
        driver.quit()

# ------------------------------
# Manual Login Helper
# ------------------------------
def manual_login_and_save(headless=False):
    """Open X.com, manually login, then save cookies for automated actions."""
    driver = start_driver(headless=headless)
    driver.get("https://x.com/login")
    input("✅ Login manually in the opened browser, then press Enter here...")
    save_cookies(driver)
    driver.quit()
    print("✅ Cookies saved for automated actions.")
