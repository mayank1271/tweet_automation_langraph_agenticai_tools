# run_once_login.py
import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

PROFILE_DIR = Path("profiles/x_persistent_profile")

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False
        )
        page = await browser.new_page()
        await page.goto("https://x.com/home")
        print("➡️  Login manually, complete OTP/2FA if asked.")
        input("Press ENTER after successful login (Home feed visible)...")
        print("✅ Logged-in session permanently stored in:", PROFILE_DIR)
        await page.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
