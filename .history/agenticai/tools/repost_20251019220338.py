import time
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

COOKIE_FILE = Path(r"C:\Users\mayank manjhi\Downloads\(1)lang,rag,ai\profiles\uc_x_cookies.json")

def apply_saved_cookies(driver):
    cookies = json.load(COOKIE_FILE.open())
    for cookie in cookies:
        driver.add_cookie(cookie)

def repost_tweet(tweet_url):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    try:
        # Load base page & cookies
        driver.get("https://x.com/")
        time.sleep(3)
        apply_saved_cookies(driver)
        driver.refresh()
        time.sleep(3)

        driver.get(tweet_url)
        time.sleep(5)
        print("🔍 Searching for Repost button...")

        # ✅ Locate Repost button
        repost_button = driver.find_element(By.XPATH, "//button[@data-testid='retweet']")
        ActionChains(driver).move_to_element(repost_button).pause(0.5).click().perform()
        time.sleep(2)

        # ✅ Click "Repost" option in popup menu
        repost_option = driver.find_elements(By.XPATH, "//span[text()='Repost']")
        if repost_option:
            repost_option[0].click()
            time.sleep(2)
            print(f"🔁 Successfully reposted: {tweet_url}")
        else:
            print("⚠️ Popup 'Repost' option not found — maybe already reposted or slow load.")

    except Exception as e:
        print(f"❌ Error during repost: {e}")

    finally:
        try:
            driver.quit()
        except Exception:
            pass

# ✅ Optional standalone test
if __name__ == "__main__":
    test_url = "https://x.com/Lap_surgeon/status/1979812678228185319"
    repost_tweet(test_url)
