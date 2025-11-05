from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

profile_path = r"C:\Users\mayank manjhi\AppData\Local\Google\Chrome\User Data\Profile 5"

options = Options()
options.add_argument(f"--user-data-dir={profile_path}")  # Use your profile path
options.add_argument("--profile-directory=Profile 5")   # Profile folder
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)

driver.get("https://x.com/home")
time.sleep(10)  # Wait for page to load

print("✅ Chrome launched with your profile and logged in.")
