import asyncio
from playwright.async_api import async_playwright, TimeoutError
from agenticai.tools.utils import apply_saved_cookies

async def comment_tweet(tweet_url, comment_text):
    """
    Navigates to a specific tweet URL, and posts a comment using robust locators.
    First, it verifies if the saved cookies result in a successful login.
    """
    print(f"📨 Inside comment_tweet for: {tweet_url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        # 1. Apply saved cookies
        print("🍪 Applying saved cookies...")
        await apply_saved_cookies(context)
        page = await context.new_page()

        try:
            # 2. Verify login status by visiting the home page first
            print("🔐 Verifying login status by visiting x.com/home...")
            await page.goto("https://x.com/home", timeout=60000, wait_until="domcontentloaded")
            
            # Check for an element that only appears when logged in, like the main tweet composer.
            # If this fails, it means the cookies are invalid or expired.
            try:
                # The tweet composer is a good indicator of being logged in.
                composer = page.get_by_test_id('tweetTextarea_0')
                await composer.wait_for(timeout=15000) # Wait for 15 seconds
                print("✅ Login verified successfully!")
            except TimeoutError:
                print("❌ Login verification failed! The saved cookies might be invalid or expired.")
                print("Please re-generate and save your login cookies.")
                await page.screenshot(path="login_verification_failed.png", full_page=True)
                return # Stop the execution if login fails

            # 3. If login is successful, proceed to the tweet URL
            print(f"➡️ Navigating to tweet: {tweet_url}")
            await page.goto(tweet_url, timeout=60000, wait_until="domcontentloaded")
            
            print("⏳ Waiting for the main tweet to load...")
            main_tweet = page.locator('article[data-testid="tweet"]').first
            await main_tweet.wait_for(timeout=15000)
            print("✅ Tweet loaded.")

            # 4. Click the reply icon
            print("⏳ Looking for the reply icon...")
            reply_icon = main_tweet.get_by_test_id('reply')
            await reply_icon.click()
            print("🖱️ Clicked the reply icon.")

            # 5. Locate and fill the reply textbox
            print("⏳ Looking for the reply text box...")
            textbox = page.get_by_test_id('tweetTextarea_0')
            await textbox.wait_for(timeout=10000)
            print("✅ Text box found.")
            await textbox.fill(comment_text)
            print(f"✍️ Typed comment: '{comment_text}'")
            
            # 6. Click the final Reply button
            reply_btn = page.get_by_test_id('tweetButton')
            await reply_btn.click()
            print("🚀 Clicked the final 'Reply' button.")

            # 7. Confirm the reply was sent
            await page.get_by_text("Your post was sent.").wait_for(timeout=10000)
            print(f"✅💬 Comment posted successfully!")

        except TimeoutError:
            print("❌ A timeout occurred during the commenting process.")
            await page.screenshot(path="comment_process_timeout.png", full_page=True)
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")
            await page.screenshot(path="comment_process_error.png", full_page=True)
        finally:
            print("Closing browser.")
            await browser.close()