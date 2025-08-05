import asyncio
from playwright.async_api import async_playwright
from agenticai.tools.utils import apply_saved_cookies

async def like_tweet(tweet_url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await apply_saved_cookies(context)
        page = await context.new_page()

        await page.goto(tweet_url, timeout=60000)
        await page.wait_for_timeout(5000)

        if "login" in page.url:
            print("❌ Not logged in.")
            await browser.close()
            return

        try:
            # More reliable using role+name
            like_buttons = page.locator('button[aria-label*="Like"][data-testid="like"]')
            count = await like_buttons.count()
            print(f"🔎 Found {count} Like buttons")

            for i in range(count):
                btn = like_buttons.nth(i)
                box = await btn.bounding_box()
                if box:  # Means it's visible
                    await btn.scroll_into_view_if_needed()
                    await btn.click()
                    print(f"✅ Liked: {tweet_url}")
                    break
            else:
                raise Exception("❌ No visible like button found.")

        except Exception as e:
            await page.screenshot(path="like_debug.png", full_page=True)
            print(f"❌ Like failed: {e} (Screenshot saved to like_debug.png)")
        await browser.close()
