from playwright.sync_api import sync_playwright

def launch_persistent_browser():
    with sync_playwright() as p:
        # ✅ Custom persistent profile
        user_data_dir = "chrome_profile"

        # Launch persistent context (saves cookies, sessions)
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,   # visible for first login
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        page = browser.new_page()
        page.goto("https://x.com/home")
        input("🔐 Login manually and press Enter here...")

        print("✅ Login saved permanently in:", user_data_dir)
        print("Next runs will auto-login without asking again.")

        browser.close()

if __name__ == "__main__":
    launch_persistent_browser()
