# comment.py
from langchain.tools import BaseTool
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
    StaleElementReferenceException
)
import asyncio
import nest_asyncio
import time

nest_asyncio.apply()

class CommentTweetTool(BaseTool):
    name: str = "comment_tweet"
    description: str = "Posts a comment/reply on a tweet using an existing Chrome session via remote debugging (no new window)."

    async def _arun(self, tweet_url: str, comment_text: str):
        # Attach to EXISTING Chrome session (must be launched with --remote-debugging-port=9222)
        chrome_options = Options()
        chrome_options.debugger_address = "127.0.0.1:9222"

        # ✅ DO NOT pass any Service() or DriverManager → just connect directly
        driver = webdriver.Chrome(options=chrome_options)

        try:
            print(f"🔗 Connecting to existing Chrome session...")
            driver.get(tweet_url)
            await asyncio.sleep(5)

            comment_xpath = '//div[@data-testid="tweetTextarea_0"]'
            reply_button_xpath = '//button[@data-testid="tweetButton"]'

            for attempt in range(3):
                try:
                    textbox = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, comment_xpath))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", textbox)
                    time.sleep(0.3)
                    textbox.click()
                    textbox.clear()
                    textbox.send_keys(comment_text)
                    time.sleep(0.5)

                    # Reply button click
                    button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, reply_button_xpath))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                    time.sleep(0.3)
                    button.click()

                    print("💬 Comment posted successfully!")
                    return True

                except ElementClickInterceptedException:
                    print(f"⚠️ Comment click intercepted, retrying... Attempt {attempt+1}")
                    driver.execute_script("window.scrollBy(0, 50);")
                    time.sleep(0.5)
                except TimeoutException:
                    print("⚠️ Timeout waiting for Comment elements.")
                    return False
                except StaleElementReferenceException:
                    print("⚠️ Comment element went stale, retrying...")
                    time.sleep(0.5)

            print("❌ Failed to post comment after 3 attempts.")
            return False

        except Exception as e:
            print("⚠️ Comment action failed:", e)
            return False

        # ⚠️ DO NOT QUIT driver → keep existing Chrome alive
        # driver.quit()

    def _run(self, tweet_url: str, comment_text: str):
        return self._arun(tweet_url, comment_text)


# Instantiate tool
comment_tweet = CommentTweetTool()
