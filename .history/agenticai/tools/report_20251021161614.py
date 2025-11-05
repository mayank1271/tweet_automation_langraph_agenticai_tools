# report.py
from langchain.tools import BaseTool
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import asyncio
import time

class ReportTweetTool(BaseTool):
    name = "report_tweet"
    description = "Reports a tweet as spam/fake on X.com using an existing Chrome session connected via remote debugging."

    def _run(self, tweet_url: str):
        """Synchronous entry for LangChain."""
        return asyncio.run(self._arun(tweet_url))

    async def _arun(self, tweet_url: str):
        print(f"🚨 Connecting to Chrome session to report: {tweet_url}")

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
                actions = ActionChains(driver)

                # 1️⃣ Click the "More" button
                more_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="More" or @data-testid="caret"]'))
                )
                actions.move_to_element(more_btn).click().perform()
                time.sleep(1)

                # 2️⃣ Click "Report Post"
                report_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@data-testid="report"]//span[text()="Report post"]'))
                )
                actions.move_to_element(report_btn).click().perform()
                time.sleep(1)

                # 3️⃣ Select "Spam / Fake engagement" option
                spam_option = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//span[contains(text(),"Fake engagement") or contains(text(),"Spam")]'))
                )
                spam_option.click()
                time.sleep(1)

                # 4️⃣ Click "Done" button
                done_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="ocfSettingsListNextButton"]//span[text()="Done"]'))
                )
                actions.move_to_element(done_btn).click().perform()
                time.sleep(1)

                print(f"✅ Tweet reported successfully: {tweet_url}")
                return {"status": "success", "action": "report"}

            except Exception as e:
                print(f"❌ Error during reporting: {e}")
                driver.save_screenshot("report_debug.png")
                return {"status": "failed", "reason": str(e)}

        except Exception as e:
            print(f"🚨 Chrome session connection failed: {e}")
            return {"status": "failed", "reason": "chrome_connection_error"}

        finally:
            pass  # keep browser open to maintain session

report_tweet = ReportTweetTool()
