# report.py
import asyncio
from langchain.tools import BaseTool
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class ReportTweetTool(BaseTool):
    name: str = "report_tweet"
    description: str = "Reports a tweet on X.com using an existing Chrome session connected via remote debugging."

    def _run(self, tweet_url: str, reason: str = "Abusive or harmful content"):
        """Synchronous entry (LangChain expects this too)."""
        return asyncio.run(self._arun(tweet_url, reason))

    async def _arun(self, tweet_url: str, reason: str):
        print(f"🚨 Connecting to Chrome session to report tweet: {tweet_url}")

        options = Options()
        options.debugger_address = "127.0.0.1:9222"

        try:
            driver = webdriver.Chrome(options=options)
            driver.get(tweet_url)
            time.sleep(5)

            # ✅ Check login
            if "login" in driver.current_url.lower():
                print("❌ Not logged in.")
                return {"status": "failed", "reason": "not_logged_in"}

            try:
                # ✅ Open the tweet menu (3 dots)
                menu_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@data-testid="caret"]'))
                )
                ActionChains(driver).move_to_element(menu_button).click().perform()
                time.sleep(1)

                # ✅ Click "Report" option
                report_option = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Report")]'))
                )
                report_option.click()
                time.sleep(2)

                # ✅ Select reason dynamically if available
                try:
                    reason_element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, f'//span[contains(text(), "{reason.split()[0]}")]'))
                    )
                    reason_element.click()
                    print(f"📝 Selected reason: {reason}")
                except Exception:
                    print("⚠️ Couldn't find specific reason option, using default flow.")

                # ✅ Click next/confirm buttons (X.com usually has these)
                for _ in range(2):
                    try:
                        next_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, '//div[@role="button"]//span[contains(text(), "Next")]'))
                        )
                        next_button.click()
                        time.sleep(1)
                    except Exception:
                        pass

                # ✅ Final submit
                try:
                    submit_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, '//div[@role="button"]//span[contains(text(), "Submit")]'))
                    )
                    submit_button.click()
                    print("✅ Report submitted successfully!")
                    return {"status": "success", "action": "report", "reason": reason}
                except Exception:
                    print("⚠️ Report submitted or flow ended earlier.")
                    return {"status": "success", "action": "report_partial", "reason": reason}

            except Exception as e:
                print(f"❌ Error reporting tweet: {e}")
                driver.save_screenshot("report_debug.png")
                return {"status": "failed", "reason": str(e)}

        except Exception as e:
            print(f"🚨 Chrome session connection failed: {e}")
            return {"status": "failed", "reason": "chrome_connection_error"}

        finally:
            pass  # keep browser session alive


# ✅ Tool instance for LangChain graph
report_tweet = ReportTweetTool()


# ✅ Local test example
if __name__ == "__main__":
    test_url = "https://x.com/username/status/1234567890"
    test_reason = "Hate speech or abuse"
    result = report_tweet._run(test_url, test_reason)
    print(result)
