# tools/repost_tool.py
import asyncio
from playwright.async_api import async_playwright
from agenticai.tools.utils import apply_saved_cookies

async def repost_tweet(tweet_url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await apply_saved_cookies(context)
        page = await context.new_page()

        await page.goto(tweet_url, timeout=60000)
        await page.wait_for_timeout(5000)

        try:
            # ✅ Find visible repost button
            retweet_btns = page.locator('button[aria-label*="Repost"][data-testid="retweet"]')
            count = await retweet_btns.count()
            for i in range(count):
                btn = retweet_btns.nth(i)
                box = await btn.bounding_box()
                if box:
                    await btn.scroll_into_view_if_needed()
                    await btn.click()
                    break
            else:
                raise Exception("❌ No visible repost button found.")

            # ✅ Wait for Repost menu option
            repost_option = page.get_by_role("menuitem", name="Repost")
            await repost_option.wait_for(timeout=5000)
            await repost_option.click()

            print(f"🔁 Reposted: {tweet_url}")

        except Exception as e:
            await page.screenshot(path="repost_debug.png", full_page=True)
            print(f"❌ Repost failed: {e} (screenshot saved)")
        await browser.close()
