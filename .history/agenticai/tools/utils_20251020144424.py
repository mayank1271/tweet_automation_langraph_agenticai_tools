import time, json, os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# 🔹 Local path to save cookies
COOKIE_FILE = "x_cookies.json"

def start_driver(headless=False, use_profile=True, profile_dir="Default"):
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--start-maximized")

    if headless:
        chrome_options.add_argument("--headless=new")

    if use_profile:
        chrome_options.add_argument(r"--user-data-dir=C:\Users\mayank manjhi\AppData\Local\Google\Chrome\User Data\Profile 3")
        chrome_options.add_argument(r"--profile-directory=Default")

    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def manual_login_and_save():
    """Open X.com with your Chrome profile, confirm login, and save cookies."""
    driver = start_driver(headless=False, use_profile=True, profile_dir="Profile 3")
    print("🌐 Opening X.com ...")
    driver.get("https://x.com/home")
    time.sleep(6)

    # --- Check login status ---
    if "login" in driver.current_url.lower():
        print("🔒 Not logged in — please login manually in the opened Chrome window.")
        input("➡️ Press ENTER after logging in manually...")
        driver.get("https://x.com/home")
        time.sleep(5)

    # --- Confirm login ---
    try:
        user_elem = driver.find_element(By.XPATH, "//a[contains(@href,'/settings/profile') or contains(@href,'/home')]")
        print("✅ Logged in successfully!")
    except:
        print("⚠️ Could not confirm login automatically — check window manually.")
    
    # --- Save cookies to JSON file ---
    cookies = driver.get_cookies()
    with open(COOKIE_FILE, "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=2)
    print(f"🍪 Cookies saved to: {COOKIE_FILE}")

    input("✅ Press ENTER to close Chrome...")
    driver.quit()


def apply_saved_cookies(driver, path=COOKIE_FILE):
    """Apply cookies to a new driver session."""
    if not os.path.exists(path):
        print("⚠️ No cookies file found, please run manual_login_and_save() first.")
        return
    with open(path, "r", encoding="utf-8") as f:
        cookies = json.load(f)
    driver.get("https://x.com/")
    for cookie in cookies:
        if 'sameSite' in cookie and cookie['sameSite'] == 'None':
            cookie['sameSite'] = 'Lax'
        try:
            driver.add_cookie(cookie)
        except Exception:
            pass
    print("✅ Cookies applied successfully.")


if __name__ == "__main__":
    manual_login_and_save()
