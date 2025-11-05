import asyncio
import os
import re
import json
import pytz
import subprocess
import schedule
from datetime import datetime, timedelta, timezone
from playwright.async_api import async_playwright, TimeoutError
from pathlib import Path
import pandas as pd

# === CONFIG ===
COOKIES_JSON_PATH = Path("profiles/x_cookies.json")  # manually copied cookies JSON
IST = pytz.timezone("Asia/Kolkata")
os.makedirs("railways/images", exist_ok=True)
os.makedirs("railways/videos", exist_ok=True)

# === HELPERS ===
async def load_cookies(context):
    """Load cookies from JSON and convert expires to int timestamp for Playwright."""
    if not COOKIES_JSON_PATH.exists():
        raise FileNotFoundError("❌ x_cookies.json not found. Export cookies first.")

    with open(COOKIES_JSON_PATH, "r") as f:
        cookies = json.load(f)

    for c in cookies:
        if "expires" in c and isinstance(c["expires"], str):
            try:
                dt = datetime.fromisoformat(c["expires"].replace("Z", "+00:00"))
                c["expires"] = int(dt.replace(tzinfo=timezone.utc).timestamp())
            except Exception as e:
                print(f"⚠️ Failed to parse expires for cookie {c.get('name')}: {e}")
                c.pop("expires", None)

    await context.add_cookies(cookies)
    print("✅ Cookies loaded into context.")

async def ensure_login(page):
    """Check login state via composer or home redirection."""
    try:
        await page.goto("https://x.com/home", timeout=60000)
        await asyncio.sleep(3)
        if "login" in page.url.lower():
            raise RuntimeError("❌ Not logged in. Cookies may be expired.")
        await page.wait_for_selector('[data-testid="tweetTextarea_0"], textarea[aria-label="Tweet text"]', timeout=5000)
        print("✅ Logged-in session verified.")
    except TimeoutError:
        print("⚠️ Login check timeout, but continuing (assuming valid session).")

async def scroll_and_collect(page, existing_urls):
    tweet_data, seen = [], set()
    for _ in range(40):
        tweets = await page.query_selector_all('article[data-testid="tweet"]')
        for t in tweets:
            try:
                time_elem = await t.query_selector("time")
                if not time_elem:
                    continue
                url = await time_elem.evaluate("n => n.parentElement.href")
                if url in seen or url in existing_urls:
                    continue
                seen.add(url)
                text_elem = await t.query_selector('[data-testid="tweetText"]')
                text = await text_elem.inner_text() if text_elem else ""
                author_elem = await t.query_selector('div[dir="ltr"] span')
                author = await author_elem.inner_text() if author_elem else ""
                tweet_data.append({
                    "datetime": datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S"),
                    "author": author,
                    "text": text,
                    "url": url,
                    "hashtags": ", ".join(re.findall(r"#\w+", text)),
                })
            except:
                continue
        await page.keyboard.press("PageDown")
        await asyncio.sleep(3)
    return tweet_data

async def scrape_and_save():
    user_ids = ["railminindia", "irctcofficial", "railwayseva", "ashwinivaishnaw"]
    until_utc = datetime.utcnow()
    since_utc = until_utc - timedelta(days=2)
    outfile = "mentions_output.xlsx"
    existing = set()

    if os.path.exists(outfile):
        try:
            df = pd.read_excel(outfile)
            existing = set(df["posturl"].dropna().tolist())
        except:
            pass

    all_tweets = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context()
        await load_cookies(ctx)  # <-- load cookies into context

        page = await ctx.new_page()
        await ensure_login(page)

        for uid in user_ids:
            url = f"https://x.com/search?q=%40{uid}%20since%3A{since_utc.strftime('%Y-%m-%d')}&src=typed_query&f=live"
            print(f"🔍 Searching tweets for @{uid} ...")
            try:
                await page.goto(url, timeout=60000)
                await asyncio.sleep(5)
                all_tweets.extend(await scroll_and_collect(page, existing))
            except TimeoutError:
                print(f"⚠️ Timeout loading search page for @{uid}, skipping.")

        await browser.close()

    df_new = pd.DataFrame([{
        "s.no": i + 1,
        "date-time": t["datetime"],
        "social-media": "X",
        "content_text": t["text"],
        "hashtag": t["hashtags"],
        "posturl": t["url"],
        "author": t["author"],
    } for i, t in enumerate(all_tweets)])

    if os.path.exists(outfile):
        old = pd.read_excel(outfile)
        df_new = pd.concat([old, df_new], ignore_index=True).drop_duplicates("posturl")
        df_new["s.no"] = range(1, len(df_new) + 1)

    df_new.to_excel(outfile, index=False)
    print(f"✅ Updated {outfile} ({len(df_new)} tweets)")

async def scheduler():
    await scrape_and_save()
    schedule.every(5).minutes.do(lambda: asyncio.create_task(scrape_and_save()))
    while True:
        schedule.run_pending()
        await asyncio.sleep(30)
        if os.path.exists("mentions_output.xlsx"):
            subprocess.run(["python", "media_downloader.py"], check=True)
            subprocess.run(["python", "frame_extractor.py"], check=True)

if __name__ == "__main__":
    asyncio.run(scheduler())
