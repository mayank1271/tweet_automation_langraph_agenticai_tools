# agenticai/tools/like.py
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import undetected_chromedriver as uc
from langchain.tools import Tool

# ✅ Safe import for utils
try:
    from .utils import apply_saved_cookies  # relative import
except ImportError:
    from utils import apply_saved_cookies   # fallback

def start_driver(headless=True):
    options = uc.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=options)
    driver.set_page_load_timeout(60)
    return driver

def like_tweet(tweet_url):
    driver = start_driver(headless=True)  # set True to hide browser
    try:
        # Load cookies
        apply_saved_cookies(driver)

        driver.get(tweet_url)
        time.sleep(5)

        # Check login
        if "login" in driver.current_url.lower():
            print("❌ Not logged in. Please check cookies.")
            return

        # Locate like buttons
        try:
            buttons = driver.find_elements(By.XPATH, '//div[@data-testid="like"]//ancestor::div[@role="button"]')
            for btn in buttons:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                    ActionChains(driver).move_to_element(btn).click(btn).perform()
                    print(f"✅ Liked: {tweet_url}")
                    break
                except (ElementClickInterceptedException, Exception):
                    continue
            else:
                print("❌ No clickable like button found.")
        except NoSuchElementException:
            print("❌ Like button not found.")
    finally:
        driver.quit()

# ✅ LangChain Tool
like_tool = Tool.from_function(
    name="like_tweet",
    func=like_tweet,
    description="Like a tweet on Twitter using Selenium given its URL.",
)

# ✅ Optional standalone test
if __name__ == "__main__":
    test_url = "https://x.com/some_tweet_url"
    like_tweet(test_url)
