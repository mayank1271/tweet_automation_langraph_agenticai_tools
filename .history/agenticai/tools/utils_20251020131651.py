import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# --- Path for cookies ---
COOKIE_FILE = "cookies.json"

# --- Function to start Chrome driver ---
def start_driver(headless=False, use_profile=True, profile_dir="SeleniumProfile"):
    options = webdriver.ChromeOptions()
    
    if headless:
        options.add_argument("--headless=new")
    
    # Dedicated profile folder
    if use_profile:
        user_data_dir = os.path.join(os.getcwd(), profile_dir)
        os.makedirs(user_data_dir, exist_ok=True)
        options.add_argument(f"--user-data-dir={user_data_dir}")
    
    service = Service()  # assumes chromedriver in PATH
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# --- Manual login and save cookies ---
def manual_login_and_save():
    driver = start_driver(headless=False, use_profile=True, profile_dir="SeleniumProfile")
    print("🌐 Opening X.com ...")
    driver.get("https://x.com/home")
    time.sleep(5)
    
    # Check if login is required
    if "login" in driver.current_url.lower():
        print("🔒 Not logged in — please login manually in the opened Chrome window.")
        input("➡️ Press ENTER after logging in manually...")
        driver.get("https://x.com/home")
        time.sleep(3)
    
    # Confirm login
    try:
        user_elem = driver.find_element(By.XPATH, "//a[contains(@href,'/settings/profile') or contains(@href,'/home')]")
        print("✅ Logged in successfully!")
    except:
        print("⚠️ Could not confirm login automatically — check window manually.")
    
    # Save cookies
    cookies = driver.get_cookies()
    with open(COOKIE_FILE, "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=2)
    print(f"🍪 Cookies saved to: {COOKIE_FILE}")
    
    input("✅ Press ENTER to close Chrome...")
    driver.quit()

# --- Apply saved cookies for auto login ---
def apply_saved_cookies(driver, path=COOKIE_FILE):
    if not os.path.exists(path):
        print("⚠️ No cookies file found, please run manual_login_and_save() first.")
        return
    
    driver.get("https://x.com/")
    with open(path, "r", encoding="utf-8") as f:
        cookies = json.load(f)
    
    for cookie in cookies:
        if 'sameSite' in cookie and cookie['sameSite'] == 'None':
            cookie['sameSite'] = 'Lax'
        try:
            driver.add_cookie(cookie)
        except Exception:
            pass
    
    print("✅ Cookies applied successfully.")
    driver.refresh()
    time.sleep(3)

# --- Example usage ---
if __name__ == "__main__":
    if not os.path.exists(COOKIE_FILE):
        manual_login_and_save()
    else:
        driver = start_driver(headless=False, use_profile=True, profile_dir="SeleniumProfile")
        apply_saved_cookies(driver)
        print("🚀 You are now logged in automatically!")
        input("Press ENTER to close Chrome...")
        driver.quit()
