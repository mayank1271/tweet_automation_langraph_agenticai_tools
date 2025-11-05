from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, StaleElementReferenceException
import time

def safe_comment(driver, comment_xpath, comment_button_xpath, text, timeout=10):
    """
    Safely posts a comment/reply on a tweet.
    Waits for textbox and button, scrolls into view, retries if click intercepted.
    """
    for attempt in range(3):
        try:
            # Wait until comment textbox is present
            textbox = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, comment_xpath))
            )
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", textbox)
            time.sleep(0.2)
            textbox.click()
            textbox.clear()
            textbox.send_keys(text)
            time.sleep(0.2)
            
            # Wait for Reply button and click
            button = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, comment_button_xpath))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(0.2)
            button.click()
            
            print("💬 Comment posted successfully!")
            return True
        except ElementClickInterceptedException:
            print(f"⚠️ Comment click intercepted, retrying... Attempt {attempt+1}")
            driver.execute_script("window.scrollBy(0, 50);")
            time.sleep(0.5)
        except TimeoutException:
            print(f"⚠️ Timeout waiting for Comment elements")
            return False
        except StaleElementReferenceException:
            print("⚠️ Comment element went stale, retrying...")
            time.sleep(0.5)
    print("❌ Failed to post comment after 3 attempts.")
    return False

# -------------------------
# Example usage:

driver = webdriver.Chrome()  # or your existing driver
tweet_url = "https://x.com/AbhishekTyagi_/status/1975099057392738599"
driver.get(tweet_url)

# Replace with your latest devtools xpath for comment textbox and button
comment_xpath = '//div[@data-testid="tweetTextarea_0"]'
comment_button_xpath = '//div[@data-testid="tweetButtonInline"]'

# Text to post
text = 'Well said! It\'s great to see positive changes.'

# Safe comment
safe_comment(driver, comment_xpath, comment_button_xpath, text)
