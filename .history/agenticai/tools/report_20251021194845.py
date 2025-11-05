# report.py
from langchain.tools import BaseTool
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import asyncio
import nest_asyncio

nest_asyncio.apply()

class ReportTweetTool(BaseTool):
    name: str = "report_tweet"
    description: str = "Reports a tweet on X.com using an existing Chrome session."

    async def _arun(self, tweet_url: str):
        chrome_options = Options()
        chrome_options.debugger_address = "127.0.0.1:9222"
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        try:
            driver.get(tweet_url)
            await asyncio.sleep(5)

            # Example: click "More" → "Report"
            more_button = driver.find_element(By.XPATH, '//div[@data-testid="caret"]')
            more_button.click()
            await asyncio.sleep(1)

            report_button = driver.find_element(By.XPATH, '//div[text()="Report Tweet"]')
            report_button.click()
            print("🚨 Tweet reported successfully!")

            await asyncio.sleep(2)
        except Exception as e:
            print("⚠️ Report action failed:", e)
        finally:
            driver.quit()

    def _run(self, tweet_url: str):
        return self._arun(tweet_url)

# Instantiate tool
report_tweet = ReportTweetTool()
