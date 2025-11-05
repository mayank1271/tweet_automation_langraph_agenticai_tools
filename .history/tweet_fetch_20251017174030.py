# ✅ SCRIPT 1: Tweet Fetcher using snscrape & Scheduler
import os
import re
import schedule
import pandas as pd
import pytz
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import snscrape.modules.twitter as sntwitter
import time

# --- Config ---
os.makedirs("railways/images", exist_ok=True)
os.makedirs("railways/videos", exist_ok=True)
IST = pytz.timezone("Asia/Kolkata")
OUTPUT_FILE = "mentions_output.xlsx"

def extract_hashtags(text):
    return ', '.join(re.findall(r"#\w+", text)) if text else ""

def get_user_tweets(user_id, since_datetime, until_datetime, existing_urls):
    tweets_data = []
    query = f"from:{user_id} since:{since_datetime.strftime('%Y-%m-%d')} until:{until_datetime.strftime('%Y-%m-%d')}"
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
        if i >= 200:  # limit tweets per user
            break
        if tweet.url in existing_urls:
            continue
        ist_now = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
        tweets_data.append({
            'datetime': ist_now,
            'author': tweet.user.username,
            'text': tweet.content,
            'timestamp': ist_now,
            'views': getattr(tweet, 'viewCount', 'N/A'),
            'url': tweet.url,
            'hashtags': extract_hashtags(tweet.content)
        })
    return tweets_data

def scrape_and_save():
    user_ids = ["railminindia", "irctcofficial", "railwayseva", "ashwinivaishnaw"]
    until_datetime = datetime.utcnow()
    since_datetime = until_datetime - timedelta(days=2)

    existing_urls = set()
    if os.path.exists(OUTPUT_FILE):
        try:
            df = pd.read_excel(OUTPUT_FILE)
            existing_urls = set(df['posturl'].dropna().tolist())
        except:
            pass

    all_tweets = []
    for user in user_ids:
        try:
            user_tweets = get_user_tweets(user, since_datetime, until_datetime, existing_urls)
            all_tweets.extend(user_tweets)
        except Exception as e:
            print(f"⚠️ Error fetching tweets for {user}: {e}")

    formatted_data = []
    for i, t in enumerate(all_tweets, 1):
        formatted_data.append({
            "s.no": i,
            "date-time": t.get("datetime"),
            "social-media": "Twitter",
            "content_text": t.get("text"),
            "hashtag": t.get("hashtags"),
            "posturl": t.get("url"),
            "likescount": "",
            "commentscount": "",
            "sharecounts": "",
            "viewscount": t.get("views"),
            "author": t.get("author"),
            "authorid": "",
            "tagid": "",
            "publishdatetime": t.get("timestamp"),
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
    if os.path.exists(OUTPUT_FILE):
        existing = pd.read_excel(OUTPUT_FILE)
        df = pd.concat([existing, df], ignore_index=True).drop_duplicates(subset='posturl')
        df["s.no"] = range(1, len(df)+1)

    df.to_excel(OUTPUT_FILE, index=False)
    print(f"✅ Excel updated → {OUTPUT_FILE} ({len(df)} tweets)")

    # --- Run media downloader & frame extractor ---
    if os.path.exists(OUTPUT_FILE):
        print("📥 Running media downloader...")
        subprocess.run(["python", "media_downloader.py"], check=True)
        print("🎞️ Running frame_extractor...")
        subprocess.run(["python", "frame_extractor.py"], check=True)

def scheduler():
    scrape_and_save()
    schedule.every(5).minutes.do(scrape_and_save)
    print("⏰ Scheduler running every 5 mins...")
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    scheduler()
