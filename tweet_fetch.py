# ✅ SCRIPT 1: Tweet Fetcher & Scheduler
import time
import re
import schedule
import pandas as pd
import os
import requests
import pytz
import json
import asyncio
from datetime import datetime, timedelta
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from pathlib import Path
import subprocess
import sys

# --- Config ---
COOKIE_PATH = Path("twitter_cookies.json")
os.makedirs("railways/images", exist_ok=True)
os.makedirs("railways/videos", exist_ok=True)
IST = pytz.timezone("Asia/Kolkata")

async def login_twitter_with_cookies(context, page):
    if COOKIE_PATH.exists():
        try:
            cookies = json.loads(COOKIE_PATH.read_text())
            await context.add_cookies(cookies)
            await page.goto("https://twitter.com/home", timeout=60000)
            await asyncio.sleep(5)
            if "login" not in page.url:
                print("✅ Logged in with cookies!")
                return
        except Exception as e:
            print(f"Cookie error: {e}")

    await page.goto("https://twitter.com/login", timeout=60000)
    input("Please login manually and press Enter here...")
    cookies = await context.cookies()
    COOKIE_PATH.write_text(json.dumps(cookies, indent=2))
    print("✅ Cookies saved!")


def build_search_url(user_id, since_datetime, until_datetime):
    since_str = since_datetime.strftime("%Y-%m-%d_%H:%M:%S_UTC")
    until_str = until_datetime.strftime("%Y-%m-%d_%H:%M:%S_UTC")
    return f"https://twitter.com/search?q=%40{user_id}%20since%3A{since_str}%20until%3A{until_str}&src=typed_query&f=live"

def extract_hashtags(text):
    return ', '.join(re.findall(r"#\w+", text)) if text else ""

async def scroll_and_collect(page, existing_urls):
    tweet_data, seen_urls = [], set()
    for _ in range(50):
        tweets = await page.query_selector_all('article[data-testid="tweet"]')
        for tweet in tweets:
            try:
                media_elements = await tweet.query_selector_all("img, video")
                media_urls = []
                tweet_type = "image"
                for media in media_elements:
                    src = await media.get_attribute("src")
                    if src and "profile_images" not in src and "emoji" not in src:
                        if ".mp4" in src or "video" in src:
                            tweet_type = "video"
                        media_urls.append(src)
                if not media_urls:
                    continue

                tweet_text_elem = await tweet.query_selector('[data-testid="tweetText"]')
                text = await tweet_text_elem.inner_text() if tweet_text_elem else ""
                author_elem = await tweet.query_selector('div[dir="ltr"] span')
                author = await author_elem.inner_text() if author_elem else ""
                time_elem = await tweet.query_selector('time')
                timestamp = await time_elem.get_attribute('datetime') if time_elem else ""
                tweet_url = await time_elem.evaluate("node => node.parentElement.href") if time_elem else ""
                if not tweet_url or tweet_url in seen_urls or tweet_url in existing_urls:
                    continue
                seen_urls.add(tweet_url)

                full_text = await tweet.inner_text()
                full_text = full_text.lower()
                view_match = re.search(r'(\d+(?:[.,]?\d+)?[KMB]?)\s+views?', full_text)
                views = view_match.group(1) if view_match else "N/A"
                ist_now = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')

                tweet_data.append({
                    'datetime': ist_now,
                    'author': author,
                    'text': text,
                    'timestamp': ist_now,
                    'views': views,
                    'url': tweet_url,
                    'media_paths': '',
                    'post_type': '',
                    'hashtags': extract_hashtags(text)
                })
            except: continue
        await page.keyboard.press("PageDown")
        await asyncio.sleep(4)
    return tweet_data

async def scrape_and_save():
    user_ids = ["railminindia", "irctcofficial", "railwayseva", "ashwinivaishnaw"]
    until_datetime = datetime.utcnow()
    since_datetime = until_datetime - timedelta(days=2)
    output_file = "mentions_output.xlsx"
    existing_urls = set()
    if os.path.exists(output_file):
        try:
            df = pd.read_excel(output_file)
            existing_urls = set(df['posturl'].dropna().tolist())
        except: pass
    all_tweets = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await login_twitter_with_cookies(context, page)
        for user_id in user_ids:
            await page.goto(build_search_url(user_id, since_datetime, until_datetime), timeout=60000)
            await asyncio.sleep(5)
            tweets = await scroll_and_collect(page, existing_urls)
            all_tweets.extend(tweets)
        await browser.close()
    formatted_data = []
    for i, tweet in enumerate(all_tweets, 1):
        formatted_data.append({
            "s.no": i,
            "date-time": tweet.get("datetime"),
            "social-media": "Twitter",
            "content_text": tweet.get("text"),
            "hashtag": tweet.get("hashtags"),
            "posturl": tweet.get("url"),
            "likescount": "",
            "commentscount": "",
            "sharecounts": "",
            "viewscount": tweet.get("views"),
            "author": tweet.get("author"),
            "authorid": "",
            "tagid": "",
            "publishdatetime": tweet.get("timestamp"),
            "img_path": "",
            "video_path": "",
            "post_type": "",
            "original_id": "",
            "is_duplicate": "",
            "sentimental_tone": "",
            "biased_type": "",
            "features": ""
        })
    df = pd.DataFrame(formatted_data)
    if os.path.exists(output_file):
        existing = pd.read_excel(output_file)
        df = pd.concat([existing, df], ignore_index=True).drop_duplicates(subset='posturl')
        df["s.no"] = range(1, len(df)+1)
    df.to_excel(output_file, index=False)
    print(f"✅ Excel updated → {output_file} ({len(df)} tweets)")

async def scheduler():
    await scrape_and_save()
    schedule.every(5).minutes.do(lambda: asyncio.create_task(scrape_and_save()))
    print("Scheduler running every 5 mins...")
    while True:
        schedule.run_pending()
        await asyncio.sleep(30)
        if os.path.exists("mentions_output.xlsx"):
           ###run the media downloader
            print("📥 Running media downloader...")
            subprocess.run(["python", "media_downloader.py"], check=True)
            ## run the frame_extractor
            print("running frame_extractor")
            subprocess.run(["python","frame_extractor.py"],check=True)

if __name__ == "__main__":
    asyncio.run(scheduler())
