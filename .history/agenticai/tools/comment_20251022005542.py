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

nest_asyncio.apply()

class CommentTweetTool(BaseTool):
    name: str = "comment_tweet"
    description: str = "Comments on a tweet on X.com using an existing Chrome session."

    async def _arun(self, tweet_url: str, comment_text: str):
        chrome_options = Options()
        chrome_options.debugger_address = "127.0.0.1:9222"
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        try:
            driver.get(tweet_url)
            await asyncio.sleep(5)

            # ✅ Click the reply icon (opens textbox)
            reply_icon = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="reply"]'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", reply_icon)
            reply_icon.click()
            await asyncio.sleep(2)

            # ✅ Type comment in active tweet reply box (new selector)
            textarea = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="tweetTextarea_0"]'))
            )
            textarea.click()
            textarea.send_keys(comment_text)
            print("💬 Comment typed successfully!")

            # ✅ Click the "Reply" button
            reply_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="tweetButtonInline"]'))
            )
            reply_button.click()
            print("✅ Comment posted successfully!")

            await asyncio.sleep(2)

        except Exception as e:
            print("⚠️ Comment action failed:", e)
            print("💡 Tip: If it fails, open tweet manually to check if Reply button visible in your profile.")
        finally:
            driver.quit()

    def _run(self, tweet_url: str, comment_text: str):
        asyncio.run(self._arun(tweet_url, comment_text))

# Instantiate tool
comment_tweet = CommentTweetTool()
