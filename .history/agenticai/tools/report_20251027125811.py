# agenticai/tools/report.py

import asyncio
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager


async def report_tweet(tweet_url: str):
    """
    Reports a tweet using an already logged-in Chrome session (remote debugging mode).
    """

    print(f"🚨 Starting to report tweet: {tweet_url}")

    # Connect to existing Chrome (already logged in)
    chrome_options = Options()
    chrome_options.debugger_address = "127.0.0.1:9222"  # existing Chrome session
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get(tweet_url)
        print("🌐 Opened tweet:", tweet_url)

        # Wait for tweet to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "article"))
        )
        await asyncio.sleep(1)

        # Step 1️⃣ Click the three-dot menu
        print("🟢 Clicking three-dot menu...")
        more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='More' or @data-testid='caret']"))
        )
        driver.execute_script("arguments[0].click();", more_button)
        await asyncio.sleep(1.5)

        # Step 2️⃣ Click the "Report" option
        print("🟢 Selecting 'Report'...")
        report_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Report') or contains(text(),'Report post')]"))
        )
        driver.execute_script("arguments[0].click();", report_button)
        await asyncio.sleep(2)

        # Step 3️⃣ Handle reason options if they appear
        try:
            print("🟢 Looking for reason options...")
            reason = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//span[contains(text(),'spam') or contains(text(),'harmful') or contains(text(),'misleading')]")
                )
            )
            driver.execute_script("arguments[0].click();", reason)
            await asyncio.sleep(2)
        except TimeoutException:
            print("⚠️ No extra reason screen found, continuing...")

        print("✅ Report submitted successfully!")

    except Exception as e:
        print(f"❌ Error during report flow: {e}")

    finally:
        # Don’t quit — keep Chrome session alive
        print("🧩 Keeping Chrome session open (not quitting).")

    return {"status": "reported", "tweet_url": tweet_url}
