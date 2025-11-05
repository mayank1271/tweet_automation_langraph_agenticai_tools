from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()

# Use your real Chrome user data
options.add_argument(r"--user-data-dir=C:\Users\mayank manjhi\AppData\Local\Google\Chrome\User Data")

# Specify the correct profile directory
options.add_argument("--profile-directory=ProfileManager")

options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)  # keeps Chrome open after script ends

driver = webdriver.Chrome(options=options)

driver.get("https://x.com/home")
time.sleep(20)

print("✅ Chrome launched with your real logged-in profile.")
