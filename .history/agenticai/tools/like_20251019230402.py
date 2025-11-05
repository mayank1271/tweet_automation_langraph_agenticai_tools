# agenticai/tools/like.py
import time
import traceback
import asyncio
import undetected_chromedriver as uc
from langchain.tools import Tool
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    WebDriverException,
)

# ✅ Safe import from updated utils
try:
    from .utils import apply_saved_cookies, ACTION_COOKIE_FILE
except ImportError:
    from utils import apply_saved_cookies, ACTION_COOKIE_FILE


def start_driver(headless=True):
    """Initialize undetected Chrome."""
    options = uc.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)
    driver.set_page_load_timeout(60)
    return driver


def like_tweet(tweet_url, retries=3):
    """
    Like a tweet on X.com using Selenium and updated saved cookies.
    """
    for attempt in range(1, retries + 1):
        driver = None
        try:
            driver = start_driver(headless=True)
            
            # ✅ Load cookies from the saved action cookie file
            apply_saved_cookies(driver, path=ACTION_COOKIE_FILE)

            driver.get(tweet_url)
            time.sleep(5)

            # ✅ Check if logged in
            if "login" in driver.current_url.lower():
                print("❌ Not logged in — cookies may be invalid or expired.")
                driver.quit()
                return False

            print("✅ Cookies loaded into Selenium driver.")
            print("🔍 Searching for Like button...")

            # --- Selectors to locate Like button ---
            selectors = [
                '//button[@data-testid="like"]',
                '//svg[@viewBox="0 0 24 24" and .//path[contains(@d,"16.697")]]/ancestor::button',
                '//button[contains(@aria-label,"Like")]',
                '//div[@data-testid="like"]//ancestor::button',
            ]

            like_button = None
            for sel in selectors:
                try:
                    buttons = driver.find_elements(By.XPATH, sel)
                    for btn in buttons:
                        if btn.is_displayed():
                            like_button = btn
                            break
                    if like_button:
                        break
                except Exception:
                    continue

            if not like_button:
                raise Exception("❌ No clickable like button found.")

            # --- Scroll to and click Like button ---
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", like_button)
            time.sleep(1)
            try:
                ActionChains(driver).move_to_element(like_button).click().perform()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", like_button)

            print(f"❤️ Successfully liked tweet: {tweet_url}")
            driver.quit()
            return True

        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed: {e}")
            traceback.print_exc()
            if driver:
                try:
                    driver.save_screenshot(f"like_debug_attempt{attempt}.png")
                    print(f"📸 Saved screenshot: like_debug_attempt{attempt}.png")
                    driver.quit()
                except WebDriverException:
                    pass
            time.sleep(3)

    print(f"❌ Failed to like tweet after {retries} attempts: {tweet_url}")
    return False


# ✅ LangChain Tool wrapper
like_tool = Tool.from_function(
    name="like_tweet",
    func=lambda url: asyncio.to_thread(like_tweet, url),
    description="Likes a tweet on X.com using Selenium and saved cookies. Input: tweet_url"
)


if __name__ == "__main__":
    test_url = "https://x.com/arvindkkalyan/status/1979807075791495291"
    like_tweet(test_url)
