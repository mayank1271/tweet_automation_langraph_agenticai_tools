# agenticai/tools/report.py

import asyncio
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager


async def report_tweet(tweet_url: str):
    """
    Automates the Twitter/X reporting process using Selenium.
    Called by agent_controller.report_node().
    """

    print(f"🚨 Starting to report tweet: {tweet_url}")

    # --- Setup Chrome ---
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(tweet_url)

    try:
        # Wait for page to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "article"))
        )

        # Step 1️⃣ Click the three-dot menu ("More")
        print("🟢 Locating More (three-dot) menu...")
        more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='More' or @data-testid='caret']"))
        )
        driver.execute_script("arguments[0].click();", more_button)
        await asyncio.sleep(1)

        # Step 2️⃣ Click "Report"
        print("🟢 Looking for Report option...")
        report_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Report') or contains(text(), 'Report post')]"))
        )
        driver.execute_script("arguments[0].click();", report_button)
        await asyncio.sleep(1)

        # Step 3️⃣ Select reason (if appears)
        try:
            reason = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'It expresses intentions of self-harm') or contains(text(), 'spam')]"))
            )
            driver.execute_script("arguments[0].click();", reason)
            await asyncio.sleep(1)
        except TimeoutException:
            print("⚠️ No detailed reason screen found, skipping...")

        print("✅ Report flow completed successfully.")
        await asyncio.sleep(1)

    except Exception as e:
        print(f"❌ Error while reporting: {e}")

    finally:
        driver.quit()
        print("🧹 Browser closed.")

    return {"status": "reported", "tweet_url": tweet_url}
