# tools/comment_tool.py
import asyncio
from playwright.async_api import async_playwright
from agenticai.tools.utils import apply_saved_cookies

async def comment_tweet(tweet_url, comment_text):
    print(f"📨 Inside comment_tweet for: {tweet_url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        await apply_saved_cookies(context)
        page = await context.new_page()

        await page.goto(tweet_url, timeout=60000)
        await page.wait_for_timeout(4000)

        try:
            reply_icon = page.locator('div[data-testid="reply"]')
            if await reply_icon.is_visible():
                await reply_icon.click()
                await page.wait_for_timeout(2000)

            textbox = page.locator('div[role="dialog"] div[role="textbox"]')
            await textbox.wait_for(timeout=8000)
            await textbox.click()

            # 🔥 Manual JS input trigger
            await textbox.evaluate(
                """(node, value) => {
                    const evt = new InputEvent('input', { bubbles: true });
                    node.textContent = value;
                    node.dispatchEvent(evt);
                }""",
                comment_text
            )

            await page.wait_for_timeout(1500)

            reply_btn = page.locator('div[role="dialog"] div[data-testid="tweetButtonInline"]')
            await reply_btn.wait_for(timeout=5000)
            await reply_btn.click()

            print(f"💬 Comment posted: \"{comment_text}\" on {tweet_url}")

        except Exception as e:
            await page.screenshot(path="comment_debug.png", full_page=True)
            print(f"❌ Comment failed: {e}")
        finally:
            await browser.close()
