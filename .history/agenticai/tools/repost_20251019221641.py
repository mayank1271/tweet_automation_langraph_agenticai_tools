# agenticai/tools/repost_tool.py
import time
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
from pathlib import Path

# ✅ Utils
try:
    from .utils import apply_saved_cookies
except ImportError:
    from utils import apply_saved_cookies

def start_driver(headless=False):
    """Start undetected Chrome driver."""
    options = uc.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)
    driver.set_page_load_timeout(60)
    return driver

def repost_tweet(tweet_url):
    """Repost a tweet on X.com using saved cookies."""
    try:
        driver = start_driver(headless=False)

        # ✅ Load cookies
        apply_saved_cookies(driver)

        # ✅ Verify login
        driver.get("https://x.com/home")
        time.sleep(5)
        if "login" in driver.current_url.lower():
            print("❌ Not logged in. Check cookies.")
            driver.quit()
            return False
        print("✅ Logged in successfully!")

        # ✅ Open tweet
        driver.get(tweet_url)
        time.sleep(5)
        print("🔍 Searching for Repost button...")

        # ✅ Find Repost button
        repost_btn = driver.find_element(By.XPATH, "//button[@data-testid='retweet']")
        ActionChains(driver).move_to_element(repost_btn).pause(1).click().perform()
        time.sleep(2)

        # ✅ Click "Repost" option in popup menu
        repost_option = driver.find_elements(By.XPATH, "//span[text()='Repost']")
        if repost_option:
            repost_option[0].click()
            time.sleep(2)
            print(f"🔁 Successfully reposted: {tweet_url}")
        else:
            print("⚠️ Popup 'Repost' option not found — maybe already reposted or slow load.")

        driver.quit()
        return True

    except Exception as e:
        print(f"❌ Error during repost: {e}")
        try:
            driver.save_screenshot("repost_debug.png")
            driver.quit()
        except:
            pass
        return False

# ✅ Standalone test
if __name__ == "__main__":
    test_url = "https://x.com/Lap_surgeon/status/1979812678228185319"
    repost_tweet(test_url)
