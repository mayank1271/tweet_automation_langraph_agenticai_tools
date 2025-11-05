import os
import re
import time
import pandas as pd
import pytz
import schedule
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import tweepy

# --- Config ---
IST = pytz.timezone("Asia/Kolkata")
OUTPUT_FILE = "mentions_output.xlsx"
USER_IDS = ["railminindia", "irctcofficial", "railwayseva", "ashwinivaishnaw"]

# Twitter API credentials (v2)
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAHUV1wEAAAAAN4D6pCHXJpPua%2FLOLuto3hP3YGw%3D4aQhautWw4FdCtK8oqHcKHC890cnnzbkXPGBUvVSPeVJAL684K"  # <-- Replace

# Tweepy Client
client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)

def extract_hashtags(text):
    return ', '.join(re.findall(r"#\w+", text)) if text else ""

def get_user_tweets(username, since_datetime, until_datetime, existing_urls):
    """Fetch tweets using Twitter API v2."""
    tweets_data = []

    # Get user id from username
    user_resp = client.get_user(username=username)
    if user_resp.data is None:
        print(f"⚠️ User not found: {username}")
        return tweets_data
    user_id = user_resp.data.id

    # Format dates
    start_time = since_datetime.isoformat("T") + "Z"
    end_time = until_datetime.isoformat("T") + "Z"

    # Fetch tweets
    paginator = tweepy.Paginator(
        client.get_users_tweets,
        id=user_id,
        start_time=start_time,
        end_time=end_time,
        tweet_fields=["created_at", "public_metrics", "entities"],
        expansions=["attachments.media_keys"],
        media_fields=["url", "preview_image_url", "type"],
        max_results=100
    )

    media_map = {}
    for page in paginator:
        if page.includes and "media" in page.includes:
            for m in page.includes["media"]:
                media_map[m.media_key] = m

        for t in page.data:
            url = f"https://twitter.com/{username}/status/{t.id}"
            if url in existing_urls:
                continue

            text = t.text
            hashtags = extract_hashtags(text)
            views = t.public_metrics.get("view_count", "N/A") if t.public_metrics else "N/A"

            media_urls = []
            if hasattr(t, "attachments") and t.attachments:
                for key in t.attachments.get("media_keys", []):
                    if key in media_map:
                        m = media_map[key]
                        if hasattr(m, "url") and m.url:
                            media_urls.append(m.url)
                        elif hasattr(m, "preview_image_url") and m.preview_image_url:
                            media_urls.append(m.preview_image_url)

            ist_now = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
            tweets_data.append({
                "datetime": ist_now,
                "author": username,
                "text": text,
                "timestamp": t.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "views": views,
                "url": url,
                "hashtags": hashtags,
                "media": media_urls
            })

    return tweets_data

def scrape_and_save():
    until_datetime = datetime.utcnow()
    since_datetime = until_datetime - timedelta(days=2)
    existing_urls = set()

    if os.path.exists(OUTPUT_FILE):
        try:
            df = pd.read_excel(OUTPUT_FILE)
            existing_urls = set(df["posturl"].dropna().tolist())
        except:
            pass

    all_tweets = []
    for user in USER_IDS:
        tweets = get_user_tweets(user, since_datetime, until_datetime, existing_urls)
        all_tweets.extend(tweets)

    # Format for Excel
    formatted_data = []
    for i, t in enumerate(all_tweets, 1):
        formatted_data.append({
            "s.no": i,
            "date-time": t["datetime"],
            "social-media": "Twitter",
            "content_text": t["text"],
            "hashtag": t["hashtags"],
            "posturl": t["url"],
            "likescount": "",
            "commentscount": "",
            "sharecounts": "",
            "viewscount": t["views"],
            "author": t["author"],
            "authorid": "",
            "tagid": "",
            "publishdatetime": t["timestamp"],
            "img_path": "",
            "video_path": ",".join(t["media"]),
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
        df = pd.concat([existing, df], ignore_index=True).drop_duplicates(subset="posturl")
        df["s.no"] = range(1, len(df) + 1)

    df.to_excel(OUTPUT_FILE, index=False)
    print(f"✅ Excel updated → {OUTPUT_FILE} ({len(df)} tweets)")

def scheduler():
    scrape_and_save()
    schedule.every(5).minutes.do(scrape_and_save)
    print("⏰ Scheduler running every 5 minutes...")
    while True:
        schedule.run_pending()
        time.sleep(30)
        if os.path.exists(OUTPUT_FILE):
            print("📥 Running media_downloader...")
            subprocess.run(["python", "media_downloader.py"], check=True)
            print("🎞️ Running frame_extractor...")
            subprocess.run(["python", "frame_extractor.py"], check=True)

if __name__ == "__main__":
    scheduler()
