# media_downloader.py (sync Playwright version)

import os
import pandas as pd
from pathlib import Path
from playwright.sync_api import sync_playwright
import time

# --- CONFIG ---
image_dir = "railways/images"
video_dir = "railways/videos"
os.makedirs(image_dir, exist_ok=True)
os.makedirs(video_dir, exist_ok=True)

metadata_file = "mentions_output.xlsx"
final_meta_file = "final_metadata.xlsx"

df = pd.read_excel(metadata_file)
downloaded_urls = set()
if Path(final_meta_file).exists():
    downloaded_urls = set(pd.read_excel(final_meta_file)["posturl"].astype(str).tolist())

new_rows = []

# Dynamic index naming
existing_images = [f for f in os.listdir(image_dir) if f.startswith("image") and f.endswith(".jpg")]
existing_videos = [f for f in os.listdir(video_dir) if f.startswith("video") and f.endswith(".mp4")]

img_index = max([int(f.replace("image", "").replace(".jpg", "")) for f in existing_images] or [0]) + 1
vid_index = max([int(f.replace("video", "").replace(".mp4", "")) for f in existing_videos] or [0]) + 1

# -----------------------------
def download_file(request_context, url, dest):
    try:
        resp = request_context.get(url)
        if resp.ok:
            with open(dest, "wb") as f:
                f.write(resp.body())
            return True
        else:
            print(f"❌ HTTP error {resp.status} for {url}")
            return False
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return False

def scrape_media(page, request_context, row):
    global img_index, vid_index
    url = str(row["posturl"]).strip().rstrip("/")
    if url in [u.strip().rstrip("/") for u in downloaded_urls]:
        return None

    try:
        video_links = []

        # Capture video URLs dynamically
        def handle_response(response):
            if ".mp4" in response.url:
                video_links.append(response.url)

        page.on("response", handle_response)
        page.goto(url, timeout=60000)
        page.wait_for_timeout(7000)
        page.mouse.wheel(0, 8000)
        page.wait_for_timeout(3000)

        img_paths, vid_paths = [], []

        # --- Images ---
        imgs = page.query_selector_all("img[src*='pbs.twimg.com/media']")
        for img in imgs:
            src = img.get_attribute("src")
            if not src or "profile_images" in src:
                continue
            dest = os.path.join(image_dir, f"image{img_index}.jpg")
            if download_file(request_context, src, dest):
                img_paths.append(dest)
                img_index += 1

        if img_paths:
            row["img_path"] = ", ".join(img_paths)

        # --- Videos ---
        page.wait_for_timeout(5000)
        for vurl in set(video_links):
            dest = os.path.join(video_dir, f"video{vid_index}.mp4")
            if download_file(request_context, vurl, dest):
                vid_paths.append(dest)
                vid_index += 1

        if vid_paths:
            row["video_path"] = ", ".join(vid_paths)

        return row

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return None

# -----------------------------
def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        request_context = context.request

        for _, row in df.iterrows():
            result = scrape_media(context.new_page(), request_context, row.copy())
            if result:
                new_rows.append(result)

        browser.close()

    if new_rows:
        new_df = pd.DataFrame(new_rows)
        if Path(final_meta_file).exists():
            old_df = pd.read_excel(final_meta_file)
            final_df = pd.concat([old_df, new_df], ignore_index=True)
        else:
            final_df = new_df
        final_df.to_excel(final_meta_file, index=False)
        print("✅ All media downloaded and metadata saved.")
    else:
        print("⚠️ No new media downloaded.")

if __name__ == "__main__":
    main()
