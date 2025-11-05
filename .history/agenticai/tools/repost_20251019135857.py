# agenticai/tools/repost_tool.py
import time
import json
import asyncio
import traceback
from langchain.tools import Tool
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# ✅ Safe import for utils
try:
    from .utils import COOKIE_FILE  # relative import
except ImportError:
    from utils import COOKIE_FILE   # standalone run fallback


def start_driver(headless=True):
    opts = uc.ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--start-maximized")
    driver = uc.Chrome(options=opts)
    driver.set_page_load_timeout(60)
    return driver


def load_cookies_into_driver(driver):
    """Load cookies into Selenium driver from COOKIE_FILE."""
    if not COOKIE_FILE.exists():
        raise FileNotFoundError(f"Cookie file missing: {COOKIE_FILE}")

    with open(COOKIE_FILE, "r", encoding="utf-8") as f:
        cookies = json.load(f)

    driver.get("https://x.com")
    time.sleep(2)

    for cookie in cookies:
        try:
            # Selenium expects domain without leading dot
            if cookie.get("domain", "").startswith("."):
                cookie["domain"] = cookie["domain"].lstrip(".")
            driver.add_cookie(cookie)
        except Exception:
            pass

    print("✅ Cookies loaded into browser session.")


def repost_tweet(tweet_url, retries=3):
    """
    Repost (retweet) a tweet on X.com using saved cookies (Selenium version).
    Uses undetected_chromedriver and utils.COOKIE_FILE for login persistence.
    """
    for attempt in range(1, retries + 1):
        try:
            driver = start_driver(headless=True)
            load_cookies_into_driver(driver)

            driver.get(tweet_url)
            time.sleep(5)

            if "login" in driver.current_url.lower():
                print("❌ Not logged in. Please refresh cookies via utils.")
                driver.quit()
                return False

            # --- Find Repost button ---
            repost_btns = driver.find_elements(By.CSS_SELECTOR, 'button[aria-label*="Repost"]')
            if not repost_btns:
                repost_btns = driver.find_elements(By.XPATH, "//button//*[name()='svg'][@viewBox='0 0 24 24']/ancestor::button")
            if not repost_btns:
                raise Exception("Repost button not found!")

            repost_btns[0].click()
            time.sleep(2)

            # --- Click 'Repost' from menu ---
            menu_items = driver.find_elements(By.XPATH, "//div[@role='menuitem' and .='Repost']")
            if not menu_items:
                raise Exception("Repost menu item not found!")

            menu_items[0].click()
            time.sleep(2)

            print(f"🔁 Reposted successfully: {tweet_url}")
            driver.quit()
            return True

        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed: {e}")
            traceback.print_exc()
            try:
                driver.save_screenshot(f"repost_debug_attempt{attempt}.png")
                driver.quit()
            except:
                pass
            time.sleep(3)

    print(f"❌ Failed to repost after {retries} attempts: {tweet_url}")
    return False


# ✅ LangChain Tool Wrapper
repost_tool = Tool.from_function(
    name="repost_tweet",
    func=lambda url: asyncio.to_thread(repost_tweet, url),
    description="Repost (retweet) a tweet on X.com using saved cookies (Selenium-based). Input: tweet_url"
)


# ✅ Optional standalone test
if __name__ == "__main__":
    test_url = "https://x.com/example/status/123"
    repost_tweet(test_url)
