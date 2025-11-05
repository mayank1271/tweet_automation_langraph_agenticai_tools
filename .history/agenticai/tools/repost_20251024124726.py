# tools/repost_tool.py
import asyncio
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from agenticai.tools.utils import apply_saved_cookies  # adapt to Selenium
from webdriver_manager.chrome import ChromeDriverManager
import nest_asyncio

nest_asyncio.apply()

async def repost_tweet(tweet_url):
    # Setup Chrome headless
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Apply saved cookies (you need to implement Selenium version)
    await apply_saved_cookies(driver)

    try:
        driver.get(tweet_url)
        time.sleep(5)  # wait for page to load

        # ✅ Find visible repost button (like Playwright bounding_box check)
        repost_buttons = driver.find_elements(By.XPATH, '//button[contains(@aria-label,"Repost") and @data-testid="retweet"]')
        for btn in repost_buttons:
            if btn.is_displayed():
                # Scroll into view (like Playwright)
                driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                try:
                    btn.click()
                    break
                except ElementClickInterceptedException:
                    continue
        else:
            raise Exception("❌ No visible repost button found.")

        # ✅ Wait for Repost menu item
        try:
            repost_option = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@role="menuitem" and text()="Repost"]'))
            )
            repost_option.click()
        except TimeoutException:
            raise Exception("❌ Repost menu did not appear.")

        print(f"🔁 Reposted: {tweet_url}")

    except Exception as e:
        driver.save_screenshot("repost_debug.png")
        print(f"❌ Repost failed: {e} (screenshot saved)")

    finally:
        driver.quit()
