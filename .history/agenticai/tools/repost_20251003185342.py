# agenticai/tools/repost_tool.py
import asyncio
from playwright.async_api import async_playwright
from langchain.tools import Tool

try:
    from .utils import apply_saved_cookies
except ImportError:
    from utils import apply_saved_cookies


async def repost_tweet(tweet_url: str, retries: int = 3):
    """
    Navigate to a tweet URL and perform a repost/retweet.
    Supports updated X.com DOM structure with SVG icons.
    """
    for attempt in range(1, retries + 1):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                await apply_saved_cookies(context)
                page = await context.new_page()

                await page.goto(tweet_url, timeout=60000, wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)

                if "login" in page.url:
                    print("❌ Not logged in (cookies invalid).")
                    await browser.close()
                    return False

                try:
                    # --- Try standard repost button first ---
                    repost_btn = page.locator('button[aria-label*="Repost"][data-testid="retweet"]').first
                    if not await repost_btn.count():
                        # --- Fallback: match svg repost icon ---
                        repost_btn = page.locator('button:has(svg[viewBox="0 0 24 24"])').first

                    await repost_btn.scroll_into_view_if_needed()
                    await repost_btn.click()

                    # Wait for Repost menu option
                    repost_option = page.get_by_role("menuitem", name="Repost")
                    await repost_option.wait_for(timeout=5000)
                    await repost_option.click()

                    print(f"🔁 Reposted successfully: {tweet_url}")
                    await browser.close()
                    return True

                except Exception as e:
                    await page.screenshot(path=f"repost_debug_attempt{attempt}.png", full_page=True)
                    print(f"⚠️ Attempt {attempt} failed: {e} (screenshot saved)")
                    await browser.close()

        except Exception as e:
            print(f"⚠️ Attempt {attempt} network error: {e}")
            await asyncio.sleep(2)

    print(f"❌ Failed to repost after {retries} attempts: {tweet_url}")
    return False


repost_tool = Tool.from_function(
    name="repost_tweet",
    func=repost_tweet,
    description="Repost (retweet) a tweet on Twitter given its URL. Login cookies must be valid."
)

if __name__ == "__main__":
    test_url = "https://x.com/some_tweet_url"
    asyncio.run(repost_tweet(test_url))
