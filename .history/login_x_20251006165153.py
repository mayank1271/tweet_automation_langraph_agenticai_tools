# run_once_login_retry.py
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError
import time

PROFILE_DIR = Path("profiles/x_persistent_profile")
OUT = Path("profiles/playwright_storage_state.json")

# tune these
MAX_TOTAL_WAIT_SECONDS = 600   # total time to wait for manual login (10 min)
CHECK_INTERVAL = 5             # how often to check for logged-in selector
COMPOSER_SELECTOR = '[data-testid="tweetTextarea_0"], textarea[aria-label="Tweet text"]'

async def run():
    async with async_playwright() as p:
        # launch a persistent context (fresh folder if not exists)
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
            # optional: set realistic user agent; comment/uncomment as needed
            # user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )

        page = await browser.new_page()
        await page.goto("https://x.com/home", wait_until="domcontentloaded")

        print("➡️ Browser opened. If not logged in, please login manually in the opened window.")
        print(f"➡️ Will wait up to {MAX_TOTAL_WAIT_SECONDS} seconds for a logged-in indicator...")

        start = time.time()
        logged_in = False
        last_url = None

        while time.time() - start < MAX_TOTAL_WAIT_SECONDS:
            try:
                last_url = page.url
                # If go to home and not forced to /login, check for composer
                if "login" not in last_url.lower():
                    # try to wait for composer/test id indicating logged-in UI
                    try:
                        await page.wait_for_selector(COMPOSER_SELECTOR, timeout=3000)
                        logged_in = True
                        break
                    except TimeoutError:
                        # not found yet
                        pass
                # else, maybe on login page — let user login
            except Exception as e:
                print("⏱️ check error:", e)

            # snapshot URL for debugging
            print(f"Waiting... current URL: {page.url}")
            await asyncio.sleep(CHECK_INTERVAL)

        if not logged_in:
            print("❌ Did not detect logged-in state within timeout.")
            print("Suggestion: Try again after switching network (mobile hotspot) or wait 30-60 minutes.")
            # keep browser open so user can attempt manual login before quitting
            input("Press ENTER to close browser and exit (or close browser manually to keep profile): ")

        else:
            # save storage state (cookies + localStorage)
            await browser.storage_state(path=str(OUT))
            print(f"✅ Detected logged-in UI. Saved storage_state to: {OUT}")
            print("You can now use this storage_state in your automated scripts as 'storage_state' value.")
            # optionally keep browser open or close
            await page.wait_for_timeout(500)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
