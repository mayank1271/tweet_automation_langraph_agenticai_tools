# save_as_storage_state.py
import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir="profiles/x_persistent_profile",
            headless=False
        )
        page = await browser.new_page()
        await page.goto("https://x.com/home", wait_until="domcontentloaded")
        input("➡️ Login manually and press ENTER when done...")
        await browser.storage_state(path="x_storage_state.json")
        print("✅ Saved cookies to x_storage_state.json")
        await browser.close()

asyncio.run(run())
