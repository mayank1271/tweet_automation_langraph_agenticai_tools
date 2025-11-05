import asyncio
from playwright.async_api import async_playwright, TimeoutError
from agenticai.tools.utils import apply_saved_cookies

async def comment_tweet(tweet_url, comment_text):
    """
    Navigates to a specific tweet URL, and posts a comment using robust locators.
    """
    print(f"📨 Inside comment_tweet for: {tweet_url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        await apply_saved_cookies(context)
        page = await context.new_page()

        try:
            await page.goto(tweet_url, timeout=60000, wait_until="domcontentloaded")
            
            # Wait for the main tweet article to be visible before interacting
            print("⏳ Waiting for the main tweet to load...")
            # First, get a handle on the main tweet to scope our actions
            main_tweet = page.locator('article[data-testid="tweet"]').first
            await main_tweet.wait_for(timeout=15000)
            print("✅ Tweet loaded.")

            # 1. Click the reply icon within the main tweet for better accuracy
            # We locate the reply icon INSIDE the main tweet to avoid clicking the wrong one.
            print("⏳ Looking for the reply icon...")
            reply_icon = main_tweet.get_by_test_id('reply') # Using get_by_test_id is a modern and clean way
            await reply_icon.click()
            print("🖱️ Clicked the reply icon.")

            # 2. Locate the reply textbox that appears after the click
            # The 'tweetTextarea_0' test-id is often more specific to the reply composer's textarea.
            print("⏳ Looking for the reply text box...")
            textbox = page.get_by_test_id('tweetTextarea_0')
            await textbox.wait_for(timeout=10000) # Increased timeout slightly for safety
            print("✅ Text box found.")

            # 3. Fill the textbox and click the Reply button
            await textbox.fill(comment_text)
            print(f"✍️ Typed comment: '{comment_text}'")
            
            # Use get_by_test_id for the final reply button as well.
            # Playwright will find the correct one that is enabled in the reply dialog.
            reply_btn = page.get_by_test_id('tweetButton')
            await reply_btn.click()
            print("🚀 Clicked the final 'Reply' button.")

            # Confirm the reply was sent by looking for the confirmation message
            await page.get_by_text("Your post was sent.").wait_for(timeout=10000)
            print(f"✅💬 Comment posted successfully!")

        except TimeoutError:
            print("❌ A timeout occurred. The page structure may have changed or the element was not found in time.")
            # Saving screenshot with a more descriptive name
            await page.screenshot(path="comment_debug_timeout_failed.png", full_page=True)
            print("📸 Screenshot saved to comment_debug_timeout_failed.png")
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")
            await page.screenshot(path="comment_debug_error.png", full_page=True)
        finally:
            print("Closing browser.")
            await browser.close()