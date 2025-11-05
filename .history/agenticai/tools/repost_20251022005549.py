# repost.py
from langchain.tools import BaseTool
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import asyncio
import nest_asyncio

nest_asyncio.apply()

class RepostTweetTool(BaseTool):
    name: str = "repost_tweet"
    description: str = "Reposts a tweet on X.com using an existing Chrome session."

    async def _arun(self, tweet_url: str):
        chrome_options = Options()
        chrome_options.debugger_address = "127.0.0.1:9222"
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        try:
            driver.get(tweet_url)
            await asyncio.sleep(5)
            driver.execute_script("window.scrollBy(0, 400);")

            # ✅ Updated repost button locator (2025 verified)
            repost_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="retweet"]'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", repost_button)
            repost_button.click()
            print("🔁 Repost button clicked!")

            # ✅ Confirm repost (the popup 'Retweet' button)
            confirm_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@data-testid="retweetConfirm"]'))
            )
            confirm_button.click()
            print("✅ Tweet reposted successfully!")

            await asyncio.sleep(2)

        except Exception as e:
            print("⚠️ Repost action failed:", e)
            print("💡 Tip: ensure tweet fully visible, or logged in to same Chrome profile.")
        finally:
            driver.quit()

    def _run(self, tweet_url: str):
        asyncio.run(self._arun(tweet_url))

# Instantiate tool
repost_tweet = RepostTweetTool()
