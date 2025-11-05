# ✅ SCRIPT: Tweet Fetcher using Twitter API (Tweepy v2)
import os
import re
import time
import json
import pytz
import schedule
import pandas as pd
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import tweepy

# --- Config ---
IST = pytz.timezone("Asia/Kolkata")
COOKIE_PATH = Path("x_cookies.json")  # Not used here but kept for backward compatibility
os.makedirs("railways/images", exist_ok=True)
os.makedirs("railways/videos", exist_ok=True)

# --- Twitter API Setup ---
# Make sure you have Bearer Token for Twitter API v2
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAHUV1wEAAAAAN4D6pCHXJpPua%2FLOLuto3hP3YGw%3D4aQhautWw4FdCtK8oqHcKHC890cnnzbkXPGBUvVSPeVJAL684K"  # <--- Replace with your token
client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)

# --- Extract Hashtags ---
def extract_hashtags(text):
    return ', '.join(re.findall(r"#\w+", text)) if text else ""

# --- Get Tweets for a User ---
def get_user_tweets(username, since_datetime, until_datetime, existing_urls):
    tweets_data = []
    
    # RFC3339 compliant datetime strings
    start_time = since_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time = until_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    user = client.get_user(username=username)
    if not user.data:
        return tweets_data

    user_id = user.data.id
    paginator = tweepy.Paginator(
        client.get_users_tweets,
        id=user_id,
        start_time=start_time,
        end_time=end_time,
        tweet_fields=["created_at", "public_metrics", "entities"],
        expansions=None,
        max_results=100
    )

    for page in paginator:
        if not page.data:
            continue
        for tweet in page.data:
            tweet_url = f"https://twitter.com/{username}/status/{tweet.id}"
            if tweet_url in existing_urls:
                continue

            hashtags = ', '.join([h['tag'] for h in tweet.entities['hashtags']]) if tweet.entities and 'hashtags' in tweet.entities else ""

            ist_now = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
            views = tweet.public_metrics.get("view_count", "N/A") if hasattr(tweet, "public_metrics") else "N/A"

            tweets_data.append({
                "datetime": ist_now,
                "author": username,
                "text": tweet.text,
                "timestamp": tweet.created_at.astimezone(IST).strftime('%Y-%m-%d %H:%M:%S'),
                "views": views,
                "url": tweet_url,
                "hashtags": hashtags
            })

    return tweets_data

# --- Scraper Main ---
def scrape_and_save():
    user_ids = ["railminindia", "irctcofficial", "railwayseva", "ashwinivaishnaw"]
    until_datetime = datetime.utcnow()
    since_datetime = until_datetime - timedelta(days=2)
    output_file = "mentions_output.xlsx"
    existing_urls = set()

    if os.path.exists(output_file):
        try:
            df = pd.read_excel(output_file)
            existing_urls = set(df["posturl"].dropna().tolist())
        except:
            pass

    all_tweets = []
    for user in user_ids:
        tweets = get_user_tweets(user, since_datetime, until_datetime, existing_urls)
        all_tweets.extend(tweets)

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
        df = pd.concat([existing, df], ignore_index=True).drop_duplicates(subset="posturl")
        df["s.no"] = range(1, len(df) + 1)
    df.to_excel(output_file, index=False)
    print(f"✅ Excel updated → {output_file} ({len(df)} tweets)")

# --- Scheduler ---
def scheduler():
    scrape_and_save()
    schedule.every(5).minutes.do(scrape_and_save)
    print("⏰ Scheduler running every 5 minutes...")
    while True:
        schedule.run_pending()
        time.sleep(30)
        if os.path.exists("mentions_output.xlsx"):
            print("📥 Running media_downloader...")
            subprocess.run(["python", "media_downloader.py"], check=True)
            print("🎞️ Running frame_extractor...")
            subprocess.run(["python", "frame_extractor.py"], check=True)

if __name__ == "__main__":
    scheduler()
