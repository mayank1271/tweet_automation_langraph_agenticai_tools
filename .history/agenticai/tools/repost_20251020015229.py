# agenticai/tools/repost_tool.py
import time, traceback, asyncio
from langchain.tools import Tool
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException

try:
    from .utils import start_driver, apply_saved_cookies, ACTION_COOKIE_FILE
except ImportError:
    from utils import start_driver, apply_saved_cookies, ACTION_COOKIE_FILE

def repost_tweet(tweet_url, use_profile=True, profile_dir="Default", retries=2):
    for attempt in range(1, retries+1):
        driver = None
        try:
            driver = start_driver(headless=False, use_profile=use_profile, profile_dir=profile_dir)
            if not use_profile:
                apply_saved_cookies(driver, path=ACTION_COOKIE_FILE)
                driver.refresh()
                time.sleep(2)

            driver.get(tweet_url)
            time.sleep(5)
            if "login" in driver.current_url.lower():
                print("❌ Not logged in — cookies invalid.")
                driver.quit()
                return False

            print("🔍 Searching for Repost button...")
            repost_btn = None
            try:
                repost_btn = driver.find_element(By.XPATH, "//button[@data-testid='retweet']")
            except:
                btns = driver.find_elements(By.XPATH, "//button[contains(@aria-label,'Repost') or contains(@aria-label,'Retweet')]")
                repost_btn = btns[0] if btns else None

            if not repost_btn:
                print("❌ Repost button not found")
                driver.quit()
                return False

            ActionChains(driver).move_to_element(repost_btn).click(repost_btn).perform()
            time.sleep(1)
            # click the menu "Repost" option
            opts = driver.find_elements(By.XPATH, "//span[text()='Repost']")
            if opts:
                opts[0].click()
                time.sleep(1)
                print("🔁 Reposted:", tweet_url)
                driver.quit()
                return True
            else:
                print("⚠️ Repost option not visible in menu.")
                driver.quit()
                return False

        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed:", e)
            traceback.print_exc()
            if driver:
                try:
                    driver.save_screenshot(f"repost_err_{attempt}.png")
                    driver.quit()
                except WebDriverException:
                    pass
            time.sleep(2)
    return False

repost_tool = Tool.from_function(
    name="repost_tweet",
    func=lambda url: asyncio.to_thread(repost_tweet, url),
    description="Repost using Selenium profile or cookie fallback."
)
