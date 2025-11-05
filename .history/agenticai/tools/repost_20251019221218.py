# agenticai/tools/repost_tool.py
import time
import traceback
import asyncio
from langchain.tools import Tool
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

# ✅ Safe import for utils
try:
    from .utils import apply_saved_cookies  # synchronous cookie loader
except ImportError:
    from utils import apply_saved_cookies

def start_driver(headless=True):
    options = uc.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)
    driver.set_page_load_timeout(90)
    return driver

def verify_login(driver):
    """Check if user is logged in by looking for the tweet box on home page."""
    driver.get("https://x.com/home")
    time.sleep(7)
    try:
        driver.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetTextarea_0"]')
        print("✅ Login verified successfully!")
        return True
    except:
        print("❌ Not logged in. Check cookies.")
        return False

def repost_tweet(tweet_url, retries=3):
    """
    Repost (retweet) a tweet on X.com using Selenium + saved cookies.
    """
    for attempt in range(1, retries + 1):
        try:
            driver = start_driver(headless=True)

            # ✅ Load cookies and refresh
            driver.get("https://x.com/")
            time.sleep(3)
            apply_saved_cookies(driver)
            driver.refresh()
            time.sleep(5)

            # ✅ Verify login
            if not verify_login(driver):
                driver.quit()
                return False

            driver.get(tweet_url)
            time.sleep(7)  # wait for tweet to fully load
            print("🔍 Searching for Repost button...")

            # --- Find Repost button
            repost_btns = driver.find_elements(By.XPATH, "//button[@data-testid='retweet']")
            if not repost_btns:
                repost_btns = driver.find_elements(By.XPATH, "//button//*[name()='svg'][@viewBox='0 0 24 24']/ancestor::button")
            if not repost_btns:
                raise Exception("Repost button not found!")

            ActionChains(driver).move_to_element(repost_btns[0]).pause(1).click().perform()
            time.sleep(2)

            # --- Click 'Repost' option from popup menu
            menu_items = driver.find_elements(By.XPATH, "//span[text()='Repost']")
            if not menu_items:
                raise Exception("Repost menu item not found!")

            menu_items[0].click()
            time.sleep(3)

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
            time.sleep(5)

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
    test_url = "https://x.com/Lap_surgeon/status/1979812678228185319"
    repost_tweet(test_url)
