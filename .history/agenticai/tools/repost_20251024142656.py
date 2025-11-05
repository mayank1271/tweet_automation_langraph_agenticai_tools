import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def repost_tweet(tweet_url):
    chrome_options = Options()
    chrome_options.debugger_address = "127.0.0.1:9222"  # connect to running Chrome
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    driver.get(tweet_url)
    time.sleep(5)

    # Step 1: Click retweet/repost icon
    try:
        repost_icon = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@data-testid="retweet"]'))
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", repost_icon)
        time.sleep(0.5)
        repost_icon.click()
        print("🟢 Repost icon clicked.")
    except Exception as e:
        print(f"❌ Repost icon not found: {e}")
        return

    # Step 2: Wait for popup to appear and click the actual “Repost” option
    try:
        repost_confirm = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@role="menuitem"][.//span[text()="Repost"]]'))
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", repost_confirm)
        time.sleep(0.5)
        repost_confirm.click()
        print("✅ Tweet successfully reposted!")
    except Exception as e:
        print(f"❌ Failed to click Repost option: {e}")

if __name__ == "__main__":
    tweet_link = "https://x.com/DDNewslive/status/1981266633126793563"  # put your tweet link here
    repost_tweet(tweet_link)
