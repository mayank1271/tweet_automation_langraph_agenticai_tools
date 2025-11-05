from langchain.tools import BaseTool
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import asyncio
import nest_asyncio
nest_asyncio.apply()

class ReportTweetTool(BaseTool):
    name: str = "report_tweet"
    description: str = "Reports a tweet on X.com using an existing Chrome session."

    async def _arun(self, tweet_url: str, reason: str = "Inappropriate content"):
        chrome_options = Options()
        chrome_options.debugger_address = "127.0.0.1:9222"
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(tweet_url)
        await asyncio.sleep(5)

        try:
            more_button = driver.find_element(By.XPATH, '//div[@aria-label="More"]')
            more_button.click()
            report_option = driver.find_element(By.XPATH, '//div[@role="menuitem"][.//span[text()="Report Tweet"]]')
            report_option.click()
            reason_option = driver.find_element(By.XPATH, f'//span[text()="{reason}"]')
            reason_option.click()
            submit_button = driver.find_element(By.XPATH, '//div[@data-testid="confirmationSheetConfirm"]')
            submit_button.click()
            print("🚨 Tweet reported successfully!")
        except Exception as e:
            print("⚠️ Report action failed:", e)

        await asyncio.sleep(3)
        driver.quit()

    def _run(self, tweet_url: str, reason: str = "Inappropriate content"):
        return asyncio.create_task(self._arun(tweet_url, reason))

report_tweet = ReportTweetTool()
