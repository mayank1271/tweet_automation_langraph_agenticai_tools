# repost.py
from langchain.tools import BaseTool
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
    StaleElementReferenceException
)
from selenium.webdriver.chrome.options import Options
import time
import asyncio
import nest_asyncio

nest_asyncio.apply()

class RepostTweetTool(BaseTool):
    name: str = "repost_tweet"
    description: str = "Reposts a tweet on X.com using existing Chrome session (connected via remote debugging)."

    async def _arun(self, tweet_url: str):
        chrome_options = Options()
        chrome_options.debugger_address = "127.0.0.1:9222"  # connect to existing Chrome
        driver = webdriver.Chrome(options=chrome_options)

        try:
            driver.get(tweet_url)
            await asyncio.sleep(5)

            repost_xpath = '//div[@data-testid="retweet"]'
            confirm_xpath = '//div[@data-testid="retweetConfirm"]'

            # --- Scroll until repost visible and clickable ---
            for attempt in range(5):
                try:
                    repost_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, repost_xpath))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", repost_button)
                    time.sleep(0.4)
                    repost_button.click()
                    print("🔁 Repost button clicked!")

                    # Wait for confirmation pop-up
                    confirm_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, confirm_xpath))
                    )
                    confirm_btn.click()
                    print("✅ Tweet reposted successfully!")
                    return True
                except ElementClickInterceptedException:
                    print(f"⚠️ Click intercepted, scrolling more... (attempt {attempt+1})")
                    driver.execute_script("window.scrollBy(0, 300);")
                    time.sleep(0.6)
                except (TimeoutException, StaleElementReferenceException):
                    print("⚠️ Repost not visible yet, scrolling down...")
                    driver.execute_script("window.scrollBy(0, 400);")
                    time.sleep(0.8)
            print("❌ Failed to repost after retries.")
            return False

        except Exception as e:
            print("⚠️ Repost action failed:", e)
            return False

        # Do NOT quit driver since it's attached to your active Chrome session

    def _run(self, tweet_url: str):
        return self._arun(tweet_url)

# Instantiate tool
repost_tweet = RepostTweetTool()
