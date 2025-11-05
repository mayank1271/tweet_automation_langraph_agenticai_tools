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

    async def _arun(self, tweet_url: str, comment: str):
        chrome_options = Options()
        chrome_options.debugger_address = "127.0.0.1:9222"
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(tweet_url)
        await asyncio.sleep(5)

        try:
            comment_box = driver.find_element(By.XPATH, '//div[@data-testid="reply"]//div[@role="textbox"]')
            comment_box.click()
            comment_box.send_keys(comment)
            submit_button = driver.find_element(By.XPATH, '//div[@data-testid="tweetButtonInline"]')
            submit_button.click()
            print("💬 Comment posted successfully!")
        except Exception as e:
            print("⚠️ Comment action failed:", e)

        await asyncio.sleep(3)
        driver.quit()

    def _run(self, tweet_url: str, comment: str):
        loop = asyncio.get_event_loop()
        return loop.create_task(self._arun(tweet_url, comment))
