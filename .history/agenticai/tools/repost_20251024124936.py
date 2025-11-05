# tools/repost_tool.py
from langchain.tools import BaseTool
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
import asyncio
import nest_asyncio
import time

nest_asyncio.apply()

class RepostTweetTool(BaseTool):
    name: str = "repost_tweet"
    description: str = "Reposts a tweet on X.com using an existing Chrome session connected via remote debugging."

    async def _arun(self, tweet_url: str):
        # Setup Chrome with remote debugging (user must be logged in)
        chrome_options = Options()
        chrome_options.debugger_address = "127.0.0.1:9222"  # like like.py
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        try:
            driver.get(tweet_url)
            await asyncio.sleep(5)  # wait for page to load

            # ✅ Find visible repost button (like Playwright bounding_box check)
            repost_buttons = driver.find_elements(By.XPATH, '//button[contains(@aria-label,"Repost") and @data-testid="retweet"]')
            for btn in repost_buttons:
                if btn.is_displayed():
                    # Scroll into view (like Playwright)
                    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                    try:
                        btn.click()
                        break
                    except ElementClickInterceptedException:
                        continue
            else:
                raise Exception("❌ No visible repost button found.")

            # ✅ Wait for Repost menu item
            try:
                repost_option = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@role="menuitem" and text()="Repost"]'))
                )
                repost_option.click()
            except TimeoutException:
                raise Exception("❌ Repost menu did not appear.")

            print(f"🔁 Reposted: {tweet_url}")

        except Exception as e:
            driver.save_screenshot("repost_debug.png")
            print(f"❌ Repost failed: {e} (screenshot saved)")

        finally:
            driver.quit()

    def _run(self, tweet_url: str):
        """
        Return an awaitable for async pipelines.
        This avoids asyncio.run() conflicts inside LangGraph workflows.
        """
        return self._arun(tweet_url)


# Instantiate tool for import
repost_tweet = RepostTweetTool()
