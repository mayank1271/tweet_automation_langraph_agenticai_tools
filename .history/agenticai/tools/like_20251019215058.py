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

# ✅ Safe import
try:
    from .utils import apply_saved_cookies
except ImportError:
    from utils import apply_saved_cookies


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
    Like a tweet on X.com using Selenium and saved cookies.
    Updated to use the actual <svg> selector you found.
    """
    for attempt in range(1, retries + 1):
        driver = None
        try:
            driver = start_driver(headless=True)
            apply_saved_cookies(driver)

            driver.get(tweet_url)
            time.sleep(5)

            if "login" in driver.current_url.lower():
                print("❌ Not logged in — please update cookies.")
                return False

            print("✅ Cookies loaded into Selenium driver.")
            print("🔍 Searching for Like button...")

            # --- Updated selectors ---
            selectors = [
                # 1️⃣ Standard Twitter data-testid
                '//button[@data-testid="like"]',
                # 2️⃣ Generic SVG fallback (the one you shared)
                '//svg[@viewBox="0 0 24 24" and .//path[contains(@d,"16.697")]]/ancestor::button',
                # 3️⃣ Aria label fallback
                '//button[contains(@aria-label,"Like")]',
                # 4️⃣ Generic SVG-based fallback
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

            # --- Step 2: scroll + click ---
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
    test_url = "https://x.com/Lap_surgeon/status/1979812678228185319"
    like_tweet(test_url)
