# tools/report_tool.py
import asyncio
from playwright.async_api import async_playwright
from agenticai.tools.utils import apply_saved_cookies

async def report_tweet(tweet_url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        await apply_saved_cookies(context)
        page = await context.new_page()

        await page.goto(tweet_url, timeout=60000)
        await page.wait_for_timeout(3000)

        try:
            await page.click('div[aria-label="More"]')
            await page.get_by_text("Report Post").click()
            await page.get_by_text("It's suspicious or spam").click()
            await page.get_by_text("Next").click()
            await page.get_by_text("Submit").click()
            print(f"🚨 Reported: {tweet_url}")
        except Exception as e:
            print(f"❌ Report failed: {e}")

        await browser.close()
