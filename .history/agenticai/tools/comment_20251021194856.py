# comment.py
from langchain.tools import BaseTool
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
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

            comment_box = driver.find_element(By.XPATH, '//div[@data-testid="reply"]//div[@role="textbox"]')
            comment_box.click()
            comment_box.send_keys(comment_text)

            submit_button = driver.find_element(By.XPATH, '//div[@data-testid="replyButton"]')
            submit_button.click()
            print("💬 Commented successfully!")

            await asyncio.sleep(2)
        except Exception as e:
            print("⚠️ Comment action failed:", e)
        finally:
            driver.quit()

    def _run(self, tweet_url: str, comment_text: str):
        return self._arun(tweet_url, comment_text)

# Instantiate tool
comment_tweet = CommentTweetTool()
