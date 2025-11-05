from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

chrome_options = Options()
chrome_options.debugger_address = "127.0.0.1:9222"  # same port as Chrome

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

driver.get("https://x.com/home")
print("Current URL:", driver.current_url)

# Example: open any tweet
driver.get("https://x.com/arvindkkalyan/status/1979807075791495291")
time.sleep(3)
print("Page title:", driver.title)
