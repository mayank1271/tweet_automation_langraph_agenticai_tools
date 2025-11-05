from utils import start_driver
import time

driver = start_driver(headless=False, use_profile=True)
driver.get("https://x.com/home")
time.sleep(10)
print(driver.current_url)
input("Press ENTER to quit...")
driver.quit()
