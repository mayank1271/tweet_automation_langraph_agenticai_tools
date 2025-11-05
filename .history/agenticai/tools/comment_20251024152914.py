# comment.py
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
import time

nest_asyncio.apply()


class CommentTweetTool(BaseTool):
    name: str = "comment_tweet"
    description: str = "Comments on a tweet on X.com using an existing Chrome session connected via remote debugging."

    async def _arun(self, tweet_url: str, comment_text: str):
        # ✅ Connect to existing logged-in Chrome session
        chrome_options = Options()
        chrome_options.debugger_address = "127.0.0.1:9222"  # Run Chrome with: chrome.exe --remote-debugging-port=9222
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        try:
            print(f"📄 Opening tweet: {tweet_url}")
            driver.get(tweet_url)
            wait = WebDriverWait(driver, 15)
            await asyncio.sleep(5)  # Wait for tweet to load

            # ✅ Step 1: Locate the comment box
            comment_box = wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-testid="tweetTextarea_0"]'))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", comment_box)
            comment_box.click()
            time.sleep(0.8)
            comment_box.send_keys(comment_text)
            print(f"💬 Typed comment: {comment_text}")

            # ✅ Step 2: Wait for and click the Reply button
            reply_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="tweetButtonInline"]'))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", reply_button)
            driver.execute_script("arguments[0].click();", reply_button)
            print("✅ Reply button clicked — comment posted!")

            await asyncio.sleep(2)

        except Exception as e:
            driver.save_screenshot("comment_debug.png")
            print("⚠️ Comment action failed:", e)

        finally:
            driver.quit()

    def _run(self, tweet_url: str, comment_text: str):
        # ✅ Compatibility for sync LangChain execution
        asyncio.run(self._arun(tweet_url, comment_text))


# ✅ Instantiate the tool for LangChain
comment_tweet = CommentTweetTool()
