import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def click_repost(driver):
    try:
        # Try clicking the main repost SVG icon first
        repost_icon = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//svg[@viewBox="0 0 24 24" and contains(@class,"r-1srniue")]/ancestor::div[@role="button"]')
            )
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", repost_icon)
        time.sleep(0.5)
        repost_icon.click()
        print("✅ Clicked main Repost icon.")
        time.sleep(1)

        # Now click “Repost” from popup menu if it appears
        repost_menu = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//svg[@viewBox="0 0 24 24" and contains(@class,"r-1q142lx")]/ancestor::div[@role="menuitem"]')
            )
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", repost_menu)
        time.sleep(0.5)
        repost_menu.click()
        print("🎯 Clicked Repost from popup menu.")

    except Exception as e:
        print(f"⚠️ Repost not clickable or popup missing: {e}")

def repost_tweet(tweet_url):
    chrome_options = Options()
    chrome_options.debugger_address = "127.0.0.1:9222"  # Connect to existing Chrome debugging session
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    driver.get(tweet_url)
    time.sleep(5)
    click_repost(driver)

if __name__ == "__main__":
    tweet_link = "https://x.com/Trial168627/status/XXXXX"  # put your tweet link
    repost_tweet(tweet_link)
