from langchain.tools import tool
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import random
import os

# -----------------------------
# 🔧 CONFIGURATION
# -----------------------------
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CHROMEDRIVER_PATH = r"C:\Users\mayank manjhi\Downloads\chromedriver-win64\chromedriver.exe"

# Manual profile ka path user se liya jayega
PROFILE_PATH = r"C:\Users\mayank manjhi\AppData\Local\Google\Chrome\User Data\Mayank"  # example


# -----------------------------
# 🧠 DRIVER INITIALIZATION
# -----------------------------
def start_driver_with_profile(profile_path, headless=False):
    chrome_options = Options()
    chrome_options.binary_location = CHROME_PATH

    # Profile load karo (manual login possible)
    chrome_options.add_argument(f"user-data-dir={profile_path}")
    chrome_options.add_argument("--profile-directory=Default")

    # Stability fixes for DevToolsActivePort issue
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    if headless:
        chrome_options.add_argument("--headless=new")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1200, 900)
    return driver


# -----------------------------
# ❤️ LIKE TWEET FUNCTION
# -----------------------------
@tool("like_tweet_tool", return_direct=True)
def like_tweet(tweet_url: str, profile_path: str = PROFILE_PATH) -> str:
    """
    Likes a given tweet using an existing Chrome profile.
    Args:
        tweet_url: URL of the tweet to like.
        profile_path: Path to Chrome user data where Twitter is logged in.
    """
    try:
        driver = start_driver_with_profile(profile_path, headless=False)
        print("✅ Chrome started successfully.")
        driver.get(tweet_url)

        time.sleep(random.uniform(5, 8))  # wait for full load

        like_buttons = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Like')]")

        if like_buttons:
            like_buttons[0].click()
            time.sleep(2)
            driver.quit()
            return f"✅ Tweet liked successfully: {tweet_url}"
        else:
            driver.quit()
            return f"⚠️ Like button not found on page: {tweet_url}"

    except Exception as e:
        return f"❌ Error while liking tweet: {str(e)}"


# -----------------------------
# 🧪 TEST LOCALLY
# -----------------------------
if __name__ == "__main__":
    tweet = input("Enter tweet URL: ").strip()
    profile = input("https://x.com/arvindkkalyan/status/1979807075791495291").strip() or PROFILE_PATH
    result = like_tweet(tweet, profile)
    print(result)
