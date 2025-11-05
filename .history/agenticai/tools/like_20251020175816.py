from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

tweet_url = input("https://x.com/seokjin_updates/status/1979236753669288172")

# Attach to existing Chrome session
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

# Provide path to chromedriver if needed
driver = webdriver.Chrome(options=chrome_options)

driver.get(tweet_url)
time.sleep(3)  # wait for page to load

try:
    # Adjust selector if Twitter/X UI changes
    like_button = driver.find_element(By.XPATH, '//div[@data-testid="like"]')
    like_button.click()
    print(f"❤️ Successfully liked: {tweet_url}")
except Exception as e:
    print(f"❌ Could not like tweet: {e}")

driver.quit()
