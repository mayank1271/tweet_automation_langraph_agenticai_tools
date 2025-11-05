# agenticai/tools/like.py
import time, traceback, asyncio, os
from langchain.tools import Tool
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException, NoSuchElementException

# ---------------- CONFIG ----------------
PROFILE_PATH = r"C:\Users\mayank manjhi\AppData\Local\Google\Chrome\User Data\Profile 3"  # 👈 tumhara exact path
#CHROME_DRIVER_PATH = r"C:\Program Files\Google\Chrome\Application\chromedriver.exe"       # agar path alag hai, update this
RETRIES = 2


def start_driver_with_profile(profile_path=PROFILE_PATH, headless=False):
    """Start Chrome with given user profile path."""
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={os.path.dirname(profile_path)}")
    chrome_options.add_argument(f"--profile-directory={os.path.basename(profile_path)}")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--start-maximized")

    if headless:
        chrome_options.add_argument("--headless=new")


    driver = webdriver.Chrome(options=chrome_options)
    return driver


def like_tweet(tweet_url, retries=RETRIES):
    """
    Likes a tweet using Selenium + your logged-in Chrome profile.
    No cookies, no utils — full control from here.
    """
    for attempt in range(1, retries + 1):
        driver = None
        try:
            print(f"\n🚀 Attempt {attempt}: Liking tweet → {tweet_url}")

            # ✅ Launch Chrome with your local profile
            driver = start_driver_with_profile(PROFILE_PATH, headless=False)

            # ✅ Open tweet
            driver.get(tweet_url)
            time.sleep(5)

            # --- Login check ---
            if "login" in driver.current_url.lower():
                print("❌ Not logged in — make sure this Chrome profile is logged into X.com.")
                driver.quit()
                return False

            # --- Find Like button ---
            print("🔍 Searching for Like button...")
            like_btn = None
            try:
                like_btn = driver.find_element(By.XPATH, "//button[@data-testid='like']")
            except NoSuchElementException:
                btns = driver.find_elements(By.XPATH, "//button[contains(@aria-label,'Like')]")
                like_btn = btns[0] if btns else None

            if not like_btn:
                print("❌ Like button not found. Maybe already liked.")
                driver.quit()
                return False

            # --- Perform Like ---
            ActionChains(driver).move_to_element(like_btn).click(like_btn).perform()
            time.sleep(2)
            print(f"❤️ Successfully liked: {tweet_url}")

            driver.quit()
            return True

        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed: {e}")
            traceback.print_exc()

            if driver:
                try:
                    driver.save_screenshot(f"like_error_attempt{attempt}.png")
                    driver.quit()
                except WebDriverException:
                    pass
            time.sleep(3)

    print(f"❌ Failed to like tweet after {retries} attempts: {tweet_url}")
    return False


# ✅ LangChain-compatible tool
like_tool = Tool.from_function(
    name="like_tweet",
    func=lambda url: asyncio.to_thread(like_tweet, url),
    description="Likes a tweet on X.com using Selenium with local Chrome profile. Input: tweet_url"
)

# ---------------- MANUAL TEST ----------------
if __name__ == "__main__":
    tweet_url = input("https://x.com/arvindkkalyan/status/1979807075791495291").strip()
    like_tweet(tweet_url)
