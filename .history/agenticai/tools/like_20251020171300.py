import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, WebDriverException

# ============================================================
# 🧠 Function to start Chrome with your own profile directory
# ============================================================
def start_driver_with_profile(profile_path, headless=False):
    """Start Chrome with the given user profile directory."""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f"--user-data-dir={profile_path}")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")

    if headless:
        chrome_options.add_argument("--headless=new")

    print(f"🧭 Starting Chrome with profile: {profile_path}")
    driver = webdriver.Chrome(options=chrome_options)
    return driver


# ============================================================
# ❤️ Like a Tweet Function
# ============================================================
def like_tweet(tweet_url: str, profile_path: str, retries: int = 2) -> bool:
    """
    Opens Chrome with user's logged-in profile and likes a given tweet URL.
    """
    for attempt in range(1, retries + 1):
        driver = None
        try:
            print(f"\n🚀 Attempt {attempt}: Liking tweet → {tweet_url}")

            # Start Chrome with your user profile
            driver = start_driver_with_profile(profile_path, headless=False)
            driver.get(tweet_url)
            time.sleep(5)

            # --- Login check ---
            if "login" in driver.current_url.lower():
                print("❌ Not logged in! Make sure your Chrome profile is logged into X.")
                driver.quit()
                return False

            print("🔍 Searching for Like button...")
            like_btn = None

            try:
                # Main Like button selector
                like_btn = driver.find_element(By.XPATH, "//button[@data-testid='like']")
            except NoSuchElementException:
                # Fallback selector (sometimes label changes)
                buttons = driver.find_elements(By.XPATH, "//button[contains(@aria-label,'Like')]")
                like_btn = buttons[0] if buttons else None

            if not like_btn:
                print("❌ Like button not found — maybe already liked or selector outdated.")
                driver.quit()
                return False

            # --- Click Like ---
            ActionChains(driver).move_to_element(like_btn).click(like_btn).perform()
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
            time.sleep(2)

    print(f"❌ Failed to like tweet after {retries} attempts: {tweet_url}")
    return False


# ============================================================
# 🧪 Manual Test Section
# ============================================================
if __name__ == "__main__":
    tweet = input("Enter tweet URL: ").strip()
    profile = input("Enter your Chrome profile path: ").strip()

    if not tweet or not profile:
        print("⚠️ Missing tweet URL or profile path.")
    else:
        result = like_tweet(tweet, profile)
        print("✅ Result:", result)
