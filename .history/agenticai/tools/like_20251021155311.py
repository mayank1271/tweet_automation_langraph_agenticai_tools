# like.py
from langchain.tools import BaseTool
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class LikeTweetTool(BaseTool):
    name = "like_tweet"
    description = "Likes a tweet on X.com using an existing Chrome session connected via remote debugging."

    def _run(self, tweet_url: str):
        """Synchronous entry (LangChain expects this too)."""
        return asyncio.run(self._arun(tweet_url))

    async def _arun(self, tweet_url: str):
        print(f"🚀 Connecting to Chrome session to like tweet: {tweet_url}")

        options = Options()
        options.debugger_address = "127.0.0.1:9222"

        try:
            driver = webdriver.Chrome(options=options)
            driver.get(tweet_url)
            time.sleep(5)

            if "login" in driver.current_url.lower():
                print("❌ Not logged in.")
                return {"status": "failed", "reason": "not_logged_in"}

            try:
                # ✅ Wait and find like button
                like_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="like"]'))
                )

                aria = like_button.get_attribute("aria-label") or ""
                if "Liked" in aria:
                    print("❤️ Already liked.")
                    return {"status": "already_liked"}

                ActionChains(driver).move_to_element(like_button).click().perform()
                print("✅ Liked tweet successfully!")
                return {"status": "success", "action": "like"}

            except Exception as e:
                print(f"❌ Error clicking like: {e}")
                driver.save_screenshot("like_debug.png")
                return {"status": "failed", "reason": str(e)}

        except Exception as e:
            print(f"🚨 Chrome session connection failed: {e}")
            return {"status": "failed", "reason": "chrome_connection_error"}

        finally:
            pass  # don't close browser — keep session alive

like_tweet = LikeTweetTool()
