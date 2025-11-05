# like.py
from langchain.tools import BaseTool
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import asyncio
import nest_asyncio

nest_asyncio.apply()

class LikeTweetTool(BaseTool):
    name: str = "like_tweet"
    description: str = "Likes a tweet on X.com using an existing Chrome session connected via remote debugging."

    async def _arun(self, tweet_url: str):
        # Setup Chrome with remote debugging
        chrome_options = Options()
        chrome_options.debugger_address = "127.0.0.1:9222"
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        try:
            driver.get(tweet_url)
            await asyncio.sleep(5)  # wait for page to load

            like_button = driver.find_element(By.XPATH, '//button[@data-testid="like"]')
            like_button.click()
            print("❤️ Tweet liked successfully!")

            await asyncio.sleep(2)  # wait for action to register
        except Exception as e:
            print("⚠️ Like action failed:", e)
        finally:
            driver.quit()

    def _run(self, tweet_url: str):
        """
        Return an awaitable for async pipelines.
        This avoids asyncio.run() conflicts inside LangGraph workflows.
        """
        return self._arun(tweet_url)


# Instantiate tool for import
like_tweet = LikeTweetTool()
