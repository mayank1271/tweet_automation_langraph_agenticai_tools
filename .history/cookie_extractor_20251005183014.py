# cookie_extractor.py
import asyncio
from playwright.async_api import async_playwright
import json

async def save_cookies():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # manual login
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://x.com/login")
        print("🕒 Login manually, then press ENTER in this console once done.")
        input("➡️  Press ENTER after login is complete...")

        cookies = await context.cookies()
        with open("x_cookies.json", "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2)

        print("✅ Cookies saved to x_cookies.json")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(save_cookies())
