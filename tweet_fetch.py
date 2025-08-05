# tools/comment_tool.py
import asyncio
from playwright.async_api import async_playwright, TimeoutError
from agenticai.tools.utils import apply_saved_cookies

async def comment_tweet(tweet_url, comment_text):
    print(f"📨 Inside comment_tweet for: {tweet_url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await apply_saved_cookies(context)
        page = await context.new_page()

        try:
            await page.goto(tweet_url, timeout=60000, wait_until="domcontentloaded")
            
            # Wait for the main tweet article to be visible before interacting
            print("⏳ Waiting for the main tweet to load...")
            await page.locator('article[data-testid="tweet"]').first.wait_for(timeout=15000)
            print("✅ Tweet loaded.")

            # 1. Click the reply icon
            reply_icon = page.locator('div[data-testid="reply"]').first
            await reply_icon.click()
            print("🖱️ Clicked the reply icon.")

            # 2. Locate the reply textbox using its stable accessibility label
            # This is the most robust locator, better than data-testid or CSS classes.
            print("⏳ Looking for the reply text box...")
            textbox = page.locator('[aria-label="Tweet text"]')
            await textbox.wait_for(timeout=8000)
            print("✅ Text box found.")

            # 3. Fill the textbox with the comment and click the Reply button
            await textbox.fill(comment_text)
            print(f"✍️ Typed comment: '{comment_text}'")
            
            reply_btn = page.locator('div[data-testid="tweetButton"]')
            await reply_btn.click()
            print("🚀 Clicked the final 'Reply' button.")

            # Confirm the reply was sent by looking for the "Your post was sent" message
            await page.get_by_text("Your post was sent.").wait_for(timeout=10000)
            print(f"✅💬 Comment posted successfully!")

        except TimeoutError:
            print("❌ A timeout occurred. The page structure may have changed or the element was not found in time.")
            await page.screenshot(path="comment_debug_timeout.png", full_page=True)
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")
            await page.screenshot(path="comment_debug_error.png", full_page=True)
        finally:
            print("Closing browser.")
            await browser.close()