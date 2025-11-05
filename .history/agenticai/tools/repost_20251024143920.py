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
    description: str = "Reposts a tweet on X.com using an existing Chrome session connected via remote debugging."

    async def _arun(self, tweet_url: str):
        # ✅ Connect to already logged-in Chrome via remote debugging
        chrome_options = Options()
        chrome_options.debugger_address = "127.0.0.1:9222"  # Chrome must be running with --remote-debugging-port=9222
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        try:
            driver.get(tweet_url)
            await asyncio.sleep(5)  # Wait for tweet page to load

            # ✅ Find repost SVG and click parent button
            repost_icon = driver.find_element(
                By.XPATH,
                "//svg[@viewBox='0 0 24 24']//path[contains(@d,'M4.5 3.88l4.432 4.14')]"
            )
            repost_button = repost_icon.find_element(By.XPATH, "./ancestor::button[1]")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", repost_button)
            repost_button.click()

            await asyncio.sleep(2)

            # ✅ Click "Repost" from popup menu
            repost_menu = driver.find_element(By.XPATH, "//span[text()='Repost']")
            repost_menu.click()

            print("🔁 Tweet reposted successfully!")

            await asyncio.sleep(2)

        except Exception as e:
            driver.save_screenshot("repost_debug.png")
            print("⚠️ Repost action failed:", e)

        finally:
            driver.quit()

    def _run(self, tweet_url: str):
        """
        Return an awaitable for async pipelines.
        This avoids asyncio.run() conflicts inside LangGraph workflows.
        """
        return self._arun(tweet_url)


# ✅ Instantiate for import
repost_tweet = RepostTweetTool()
