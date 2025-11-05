# ✅ SCRIPT 1: Tweet Fetcher (Selenium Version)
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
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.options import Options


# --- Config ---
COOKIE_PATH = Path("x_cookies.json")
os.makedirs("railways/images", exist_ok=True)
os.makedirs("railways/videos", exist_ok=True)
IST = pytz.timezone("Asia/Kolkata")

# --- Initialize Chrome ---
def get_driver(headless=False):
    options = Options()
    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")

    # ✅ Automatically install & manage Edge driver
    service = EdgeService(EdgeChromiumDriverManager().install())

    # ✅ Create Edge WebDriver
    driver = webdriver.Edge(service=service, options=options)
    driver.set_page_load_timeout(60)
    print("✅ Edge WebDriver initialized successfully.")
    return driver

# --- Login via Cookies or Manual ---
def login_twitter_with_cookies(driver):
    driver.get("https://twitter.com/home")
    time.sleep(5)

    if COOKIE_PATH.exists():
        try:
            cookies = json.loads(COOKIE_PATH.read_text())

            # Convert expires → int
            for c in cookies:
                if "expires" in c and isinstance(c["expires"], str):
                    try:
                        if c["expires"].lower() != "session":
                            dt = datetime.fromisoformat(c["expires"].replace("Z", "+00:00"))
                            c["expires"] = int(dt.timestamp())
                        else:
                            c.pop("expires", None)
                    except:
                        c.pop("expires", None)

            for cookie in cookies:
                if "domain" in cookie and cookie["domain"].startswith("."):
                    cookie["domain"] = cookie["domain"].lstrip(".")
                driver.add_cookie(cookie)

            driver.get("https://twitter.com/home")
            time.sleep(5)
            if "login" not in driver.current_url:
                print("✅ Logged in with cookies!")
                return
        except Exception as e:
            print(f"⚠️ Cookie load failed: {e}")

    print("⚠️ Manual login required.")
    driver.get("https://twitter.com/login")
    input("🔑 Login manually, then press Enter here...")
    cookies = driver.get_cookies()
    COOKIE_PATH.write_text(json.dumps(cookies, indent=2))
    print("✅ Cookies saved!")


# --- Build Search URL ---
def build_search_url(user_id, since_datetime, until_datetime):
    since_str = since_datetime.strftime("%Y-%m-%d_%H:%M:%S_UTC")
    until_str = until_datetime.strftime("%Y-%m-%d_%H:%M:%S_UTC")
    return f"https://twitter.com/search?q=%40{user_id}%20since%3A{since_str}%20until%3A{until_str}&src=typed_query&f=live"


# --- Extract Hashtags ---
def extract_hashtags(text):
    return ', '.join(re.findall(r"#\w+", text)) if text else ""


# --- Scroll & Collect Tweets ---
def scroll_and_collect(driver, existing_urls):
    tweets_data = []
    seen_urls = set()
    for _ in range(50):
        articles = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
        for art in articles:
            try:
                text_elem = art.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                text = text_elem.text if text_elem else ""

                author = art.find_element(By.CSS_SELECTOR, 'div[dir="ltr"] span').text
                time_elem = art.find_element(By.TAG_NAME, 'time')
                timestamp = time_elem.get_attribute('datetime') if time_elem else ""
                tweet_url = time_elem.find_element(By.XPATH, "..").get_attribute("href") if time_elem else ""
                if not tweet_url or tweet_url in seen_urls or tweet_url in existing_urls:
                    continue

                seen_urls.add(tweet_url)
                media_elems = art.find_elements(By.CSS_SELECTOR, "img, video")
                media_urls = []
                tweet_type = "image"
                for m in media_elems:
                    src = m.get_attribute("src")
                    if src and "profile_images" not in src and "emoji" not in src:
                        if ".mp4" in src or "video" in src:
                            tweet_type = "video"
                        media_urls.append(src)

                full_text = art.text.lower()
                match = re.search(r'(\d+(?:[.,]?\d+)?[KMB]?)\s+views?', full_text)
                views = match.group(1) if match else "N/A"

                ist_now = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
                tweets_data.append({
                    "datetime": ist_now,
                    "author": author,
                    "text": text,
                    "timestamp": ist_now,
                    "views": views,
                    "url": tweet_url,
                    "hashtags": extract_hashtags(text)
                })
            except Exception:
                continue

        driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        time.sleep(4)
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
    driver = get_driver(headless=False)
    login_twitter_with_cookies(driver)

    for user_id in user_ids:
        url = build_search_url(user_id, since_datetime, until_datetime)
        driver.get(url)
        time.sleep(5)
        tweets = scroll_and_collect(driver, existing_urls)
        all_tweets.extend(tweets)

    driver.quit()

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
