from utils import start_driver
import time

driver = start_driver(headless=False, use_profile=True, profile_dir="Default")
print("🌍 Opening x.com/home...")
driver.get("https://x.com/home")
time.sleep(6)
print("📍 Current URL:", driver.current_url)
input("Press ENTER to close browser...")
driver.quit()
