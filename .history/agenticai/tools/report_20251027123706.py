# report.py
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, ElementClickInterceptedException, NoSuchElementException
)


def click_js(driver, element):
    """Force click via JavaScript (bypasses overlay issues)"""
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(0.4)
    driver.execute_script("arguments[0].click();", element)


def perform_report_action(driver, tweet_url):
    print(f"🚀 Opening tweet: {tweet_url}")
    driver.get(tweet_url)
    wait = WebDriverWait(driver, 20)

    try:
        # Wait for tweet to load
        wait.until(EC.presence_of_element_located((By.XPATH, "//article")))
        time.sleep(1)
        print("✅ Tweet loaded successfully.")
    except TimeoutException:
        print("❌ Tweet did not load.")
        return False

    # Step 1️⃣ Click on "More" (three-dot caret) button
    caret_clicked = False
    try:
        caret = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//button[@aria-label='More' and @data-testid='caret']")
        ))
        click_js(driver, caret)
        caret_clicked = True
        print("✅ Clicked 'More' caret button successfully.")
    except Exception as e:
        print(f"⚠️ Primary caret click failed: {e}")
        try:
            alt_caret = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//button[contains(@aria-label,'More')]")
            ))
            click_js(driver, alt_caret)
            caret_clicked = True
            print("✅ Clicked alternate caret button (fallback).")
        except Exception as e2:
            print(f"❌ Could not click caret at all: {e2}")

    if not caret_clicked:
        return False

    # Step 2️⃣ Wait for dropdown menu to appear
    try:
        menu = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@role='menu']")))
        print("✅ Dropdown menu opened.")
    except TimeoutException:
        print("❌ Dropdown menu did not open.")
        return False

    # Step 3️⃣ Click "Report post"
    try:
        report_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(text(),'Report post')]")
        ))
        click_js(driver, report_btn)
        print("✅ Clicked 'Report post' option.")
    except Exception as e:
        print(f"❌ Could not click 'Report post': {e}")
        return False

    # Step 4️⃣ Select reason (e.g. "It's misleading" or first available option)
    try:
        reason_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@role='button' and .//span]")))
        click_js(driver, reason_btn)
        print("✅ Selected first report reason.")
    except Exception as e:
        print(f"⚠️ Could not select reason: {e}")

    # Step 5️⃣ Confirm / Submit
    try:
        submit_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(text(),'Submit') or contains(text(),'Report')]")
        ))
        click_js(driver, submit_btn)
        print("✅ Report submitted successfully.")
    except Exception as e:
        print(f"⚠️ Submit step may have been skipped: {e}")

    print("🎯 Report flow completed.")
    return True


if __name__ == "__main__":
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager

    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # 🔧 Test with one tweet
    tweet_url = "https://x.com/ddnewsBihar/status/1982437734183842220"
    perform_report_action(driver, tweet_url)
