# repost.py
from langchain.tools import BaseTool
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import asyncio
import nest_asyncio

nest_asyncio.apply()

class RepostTweetTool(BaseTool):
    name: str = "repost_tweet"
    description: str = "Reposts (retweets) a tweet on X.com using an existing Chrome session."

    async def _arun(self, tweet_url: str):
        chrome_options = Options()
        chrome_options.debugger_address = "127.0.0.1:9222"
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        try:
            driver.get(tweet_url)
            await asyncio.sleep(5)

            repost_button = driver.find_element(By.XPATH, '//div[@data-testid="retweet"]')
            repost_button.click()
            confirm_button = driver.find_element(By.XPATH, '//div[@data-testid="retweetConfirm"]')
            confirm_button.click()
            print("🔁 Tweet reposted successfully!")

            await asyncio.sleep(2)
        except Exception as e:
            print("⚠️ Repost action failed:", e)
        finally:
            driver.quit()

    def _run(self, tweet_url: str):
        return self._arun(tweet_url)

# Instantiate tool
repost_tweet = RepostTweetTool()
