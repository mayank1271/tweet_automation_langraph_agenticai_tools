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
    description: str = "Reposts a tweet on X.com using an existing Chrome session connected via remote debugging."

    async def _arun(self, tweet_url: str):
        # ✅ Connect to existing logged-in Chrome session
        chrome_options = Options()
        chrome_options.debugger_address = "127.0.0.1:9222"  # Run Chrome with: chrome.exe --remote-debugging-port=9222
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        try:
            print(f"📄 Opening tweet: {tweet_url}")
            driver.get(tweet_url)

            wait = WebDriverWait(driver, 15)
            await asyncio.sleep(5)  # let page load properly

            # ✅ Step 1: Find and click repost button
            repost_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='retweet']"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", repost_button)
            repost_button.click()
            print("✅ Repost menu opened")

            # ✅ Step 2: Wait for and click 'Repost' option from popup
            confirm_repost = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='menuitem'][.//span[text()='Repost']]"))
            )
            confirm_repost.click()
            print("🔁 Tweet reposted successfully!")

            await asyncio.sleep(2)

        except Exception as e:
            driver.save_screenshot("repost_debug.png")
            print("⚠️ Repost action failed:", e)

        finally:
            driver.quit()

    def _run(self, tweet_url: str):
        # ✅ Compatibility for sync LangChain execution
        asyncio.run(self._arun(tweet_url))


# ✅ Instantiate the tool for LangChain
repost_tweet = RepostTweetTool()
