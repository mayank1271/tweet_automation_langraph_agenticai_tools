# tweet_fetcher_auto.py
import asyncio
import json
import os
import re
import pandas as pd
import pytz
import subprocess
import schedule
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
from pathlib import Path

COOKIE_PATH = Path(r"C:\Users\mayank manjhi\Downloads\(1)lang,rag,ai\x_cookies.json")
IST = pytz.timezone("Asia/Kolkata")
os.makedirs("railways/images", exist_ok=True)
os.makedirs("railways/videos", exist_ok=True)

async def login_x_with_cookies(context, page):
    """Load cookies silently, no manual step ever."""
    if not COOKIE_PATH.exists():
        raise FileNotFoundError("❌ Cookie file missing. Run cookie_extractor.py first.")
    cookies = json.loads(COOKIE_PATH.read_text())
    await context.add_cookies(cookies)
    await page.goto("https://x.com/home", timeout=60000)
    await asyncio.sleep(4)
    if "login" in page.url.lower():
        raise RuntimeError("❌ Cookies invalid or expired. Re-run cookie_extractor.py")

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
                media_elems = await t.query_selector_all("img, video")
                media_urls = [await m.get_attribute("src") for m in media_elems]
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
        page = await ctx.new_page()
        await login_x_with_cookies(ctx, page)
        for uid in user_ids:
            url = f"https://x.com/search?q=%40{uid}%20since%3A{since_utc.strftime('%Y-%m-%d')}&src=typed_query&f=live"
            await page.goto(url)
            await asyncio.sleep(5)
            all_tweets.extend(await scroll_and_collect(page, existing))
        await browser.close()

    df_new = pd.DataFrame([
        {
            "s.no": i + 1,
            "date-time": t["datetime"],
            "social-media": "X",
            "content_text": t["text"],
            "hashtag": t["hashtags"],
            "posturl": t["url"],
            "author": t["author"],
        } for i, t in enumerate(all_tweets)
    ])
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
