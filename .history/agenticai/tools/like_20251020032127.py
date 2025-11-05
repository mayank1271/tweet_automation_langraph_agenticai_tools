# agenticai/tools/like.py
import time, traceback, asyncio
from langchain.tools import Tool
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException, WebDriverException

# import utils
try:
    from .utils import start_driver, apply_saved_cookies, ACTION_COOKIE_FILE
except ImportError:
    from utils import start_driver, apply_saved_cookies, ACTION_COOKIE_FILE

def like_tweet(tweet_url, use_profile=True, profile_dir="Default", retries=2):
    """
    Like using profile mode if use_profile True, otherwise use action cookie JSON fallback.
    """
    for attempt in range(1, retries+1):
        driver = None
        try:
            driver = start_driver(headless=False, use_profile=use_profile, profile_dir=profile_dir)
            # If not using profile, load saved cookies JSON
            if not use_profile:
                apply_saved_cookies(driver, path=ACTION_COOKIE_FILE)
                driver.refresh()
                time.sleep(2)

            driver.get(tweet_url)
            time.sleep(5)

            if "login" in driver.current_url.lower():
                print("❌ Not logged in — cookies invalid. Try manual_login_and_save()")
                driver.quit()
                return False

            print("🔍 Searching for Like button...")
            btn = None
            try:
                btn = driver.find_element(By.XPATH, "//button[@data-testid='like']")
            except:
                # fallback
                btns = driver.find_elements(By.XPATH, "//button[contains(@aria-label,'Like')]")
                btn = btns[0] if btns else None

            if not btn:
                print("❌ Like button not found")
                driver.quit()
                return False

            ActionChains(driver).move_to_element(btn).click(btn).perform()
            time.sleep(2)
            print("❤️ Liked:", tweet_url)
            driver.quit()
            return True

        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed:", e)
            traceback.print_exc()
            if driver:
                try:
                    driver.save_screenshot(f"like_error_{attempt}.png")
                    driver.quit()
                except WebDriverException:
                    pass
            time.sleep(2)
    return False

like_tool = Tool.from_function(
    name="like_tweet",
    func=lambda url: asyncio.to_thread(like_tweet, url),
    description="Likes a tweet on X.com using Selenium and saved cookies. Input: tweet_url"
)


