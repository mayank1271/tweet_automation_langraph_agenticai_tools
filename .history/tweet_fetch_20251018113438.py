# tweet_fetch_uc.py
import time
import re
import json
import subprocess
import schedule
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta, timezone
import pytz
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from dateutil import parser as dtparser

# CONFIG
COOKIES_FILE = Path("profiles/uc_x_cookies.json")
OUT_XLSX = "mentions_output.xlsx"
IST = pytz.timezone("Asia/Kolkata")
USER_IDS = ["railminindia", "irctcofficial", "railwayseva", "ashwinivaishnaw"]

PROXY = None  # optional proxy string

def start_driver(headless=False):
    opts = uc.ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    if PROXY:
        opts.add_argument(f'--proxy-server={PROXY}')
    driver = uc.Chrome(options=opts)
    driver.set_page_load_timeout(60)
    return driver

def save_cookies_manual():
    driver = start_driver(headless=True)
    driver.get("https://x.com/login")
    input("➡️ Login manually, then press ENTER here...")
    cookies = driver.get_cookies()
    COOKIES_FILE.parent.mkdir(parents=True, exist_ok=True)
    COOKIES_FILE.write_text(json.dumps(cookies, indent=2))
    print("✅ Cookies saved to", COOKIES_FILE)
    driver.quit()

def load_cookies_into_driver(driver):
    if not COOKIES_FILE.exists():
        raise FileNotFoundError("Cookies file missing. Run save_cookies_manual() first.")
    raw = json.loads(COOKIES_FILE.read_text())
    fixed = []
    for c in raw:
        c2 = dict(c)
        if "expires" in c2 and isinstance(c2["expires"], str):
            val = c2["expires"]
            if val.lower() == "session":
                c2.pop("expires", None)
            else:
                try:
                    dt = dtparser.isoparse(val)
                    c2["expires"] = int(dt.astimezone(timezone.utc).timestamp())
                except:
                    c2.pop("expires", None)
        if "domain" in c2 and c2["domain"].startswith("."):
            c2["domain"] = c2["domain"].lstrip(".")
        fixed.append(c2)
    driver.get("https://x.com")
    time.sleep(1)
    for cookie in fixed:
        try:
            driver.add_cookie(cookie)
        except:
            pass
    print("✅ Cookies loaded into browser context.")

def build_search_url(user_id, since_date):
    return f"https://x.com/search?q=%40{user_id}%20since%3A{since_date}&src=typed_query&f=live"

def scroll_and_collect(driver, existing_urls):
    collected = []
    seen = set()
    SCROLLS = 30
    for _ in range(SCROLLS):
        articles = driver.find_elements(By.CSS_SELECTOR, "article[data-testid='tweet']")
        for art in articles:
            try:
                time_elem = art.find_element(By.TAG_NAME, "time")
                tweet_url = time_elem.find_element(By.XPATH, "..").get_attribute("href")
                if not tweet_url or tweet_url in seen or tweet_url in existing_urls:
                    continue
                seen.add(tweet_url)

                try:
                    text_elem = art.find_element(By.CSS_SELECTOR, "[data-testid='tweetText']")
                    text = text_elem.text
                except:
                    text = ""

                try:
                    author = art.find_element(By.CSS_SELECTOR, "div[dir='ltr'] span").text
                except:
                    author = ""

                media = []
                try:
                    media_elems = art.find_elements(By.CSS_SELECTOR, "img, video")
                    for m in media_elems:
                        src = m.get_attribute("src")
                        if src and "profile_images" not in src and "emoji" not in src:
                            media.append(src)
                except:
                    pass

                full_text = art.text.lower()
                m = re.search(r"(\d+(?:[.,]?\d+)?[kmb]?)\s+views?", full_text)
                views = m.group(1) if m else "N/A"

                collected.append({
                    "datetime": datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S"),
                    "author": author,
                    "text": text,
                    "url": tweet_url,
                    "hashtags": ", ".join(re.findall(r"#\w+", text)),
                    "media": media,
                    "views": views
                })
            except:
                continue
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(2)
    return collected

def scrape_and_save():
    existing = set()
    if Path(OUT_XLSX).exists():
        try:
            df_old = pd.read_excel(OUT_XLSX)
            existing = set(df_old["posturl"].dropna().tolist())
        except:
            existing = set()

    driver = start_driver(headless=False)
    try:
        try:
            load_cookies_into_driver(driver)
            driver.get("https://x.com/home")
            time.sleep(3)
            if "login" in driver.current_url.lower():
                print("⚠️ Cookies invalid; please login manually.")
                input("After login press ENTER...")
                cookies = driver.get_cookies()
                COOKIES_FILE.parent.mkdir(parents=True, exist_ok=True)
                COOKIES_FILE.write_text(json.dumps(cookies, indent=2))
                print("✅ New cookies saved.")
        except FileNotFoundError:
            print("Cookies not found. Please login manually.")
            input("After login press ENTER...")
            cookies = driver.get_cookies()
            COOKIES_FILE.parent.mkdir(parents=True, exist_ok=True)
            COOKIES_FILE.write_text(json.dumps(cookies, indent=2))
            print("✅ Cookies saved.")

        all_tweets = []
        since_date = (datetime.utcnow() - timedelta(days=2)).strftime("%Y-%m-%d")
        for uid in USER_IDS:
            url = build_search_url(uid, since_date)
            driver.get(url)
            time.sleep(5)
            all_tweets.extend(scroll_and_collect(driver, existing))

    finally:
        driver.quit()

    rows = []
    for i, t in enumerate(all_tweets, 1):
        rows.append({
            "s.no": i,
            "date-time": t["datetime"],
            "social-media": "X",
            "content_text": t["text"],
            "hashtag": t["hashtags"],
            "posturl": t["url"],
            "author": t["author"],
            "viewscount": t["views"],
            "media": ",".join(t["media"])
        })
    df = pd.DataFrame(rows)
    if Path(OUT_XLSX).exists():
        old = pd.read_excel(OUT_XLSX)
        df = pd.concat([old, df], ignore_index=True).drop_duplicates(subset="posturl")
        df["s.no"] = range(1, len(df) + 1)
    df.to_excel(OUT_XLSX, index=False)
    print(f"✅ Saved {len(df)} tweets to {OUT_XLSX}")

    # 🧩 after saving, run media downloader & frame extractor
    if Path(OUT_XLSX).exists():
        print("📥 Running media_downloader.py ...")
        subprocess.run(["python", "media_downloader.py"], check=True)
        print("🎞️ Running frame_extractor.py ...")
        subprocess.run(["python", "frame_extractor.py"], check=True)

def scheduler_loop():
    scrape_and_save()
    schedule.every(5).minutes.do(scrape_and_save)
    print("⏰ Scheduler running every 5 minutes...")
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    if not COOKIES_FILE.exists():
        print("No cookies found — opening browser for manual login and cookie save.")
        save_cookies_manual()
    scheduler_loop()
