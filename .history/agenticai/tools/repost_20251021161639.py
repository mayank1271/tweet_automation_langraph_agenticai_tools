# repost.py
import asyncio
from langchain.tools import BaseTool
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class RepostTweetTool(BaseTool):
    name: str = "repost_tweet"  # ✅ Pydantic 2.x compatible
    description: str = "Reposts (retweets) a tweet on X.com using an existing Chrome session connected via remote debugging."

    def _run(self, tweet_url: str):
        """Synchronous entry (LangChain expects this too)."""
        return asyncio.run(self._arun(tweet_url))

    async def _arun(self, tweet_url: str):
        print(f"🚀 Connecting to Chrome session to repost tweet: {tweet_url}")

        options = Options()
        options.debugger_address = "127.0.0.1:9222"

        try:
            driver = webdriver.Chrome(options=options)
            driver.get(tweet_url)
            time.sleep(5)

            # ✅ Login check
            if "login" in driver.current_url.lower():
                print("❌ Not logged in.")
                return {"status": "failed", "reason": "not_logged_in"}

            try:
                # ✅ Wait for repost button
                repost_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="retweet"]'))
                )

                aria = repost_button.get_attribute("aria-label") or ""
                if "Reposted" in aria or "Undo" in aria:
                    print("🔁 Already reposted.")
                    return {"status": "already_reposted"}

                # ✅ Click repost
                ActionChains(driver).move_to_element(repost_button).click().perform()
                time.sleep(1)

                # ✅ Choose “Repost” option from menu
                try:
                    menu_repost = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, '//div[@data-testid="retweetConfirm"]'))
                    )
                    menu_repost.click()
                except Exception:
                    # fallback if single click repost works without menu
                    pass

                print("✅ Reposted tweet successfully!")
                return {"status": "success", "action": "repost"}

            except Exception as e:
                print(f"❌ Error clicking repost: {e}")
                driver.save_screenshot("repost_debug.png")
                return {"status": "failed", "reason": str(e)}

        except Exception as e:
            print(f"🚨 Chrome session connection failed: {e}")
            return {"status": "failed", "reason": "chrome_connection_error"}

        finally:
            pass  # keep browser session alive


# ✅ Create tool instance
repost_tweet = RepostTweetTool()


# ✅ Local test
if __name__ == "__main__":
    test_url = "https://x.com/username/status/1234567890"
    result = repost_tweet._run(test_url)
    print(result)
