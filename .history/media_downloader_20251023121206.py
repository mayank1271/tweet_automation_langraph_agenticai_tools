# media_downloader.py — Final Stable Hybrid Version (Sync Playwright + Async Logic Ported)

import os
import time
import pandas as pd
from pathlib import Path
from playwright.sync_api import sync_playwright

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

# Continue naming from last index
existing_images = [f for f in os.listdir(image_dir) if f.startswith("image") and f.endswith(".jpg")]
existing_videos = [f for f in os.listdir(video_dir) if f.startswith("video") and f.endswith(".mp4")]

img_index = max([int(f.replace("image", "").replace(".jpg", "")) for f in existing_images] or [0]) + 1
vid_index = max([int(f.replace("video", "").replace(".mp4", "")) for f in existing_videos] or [0]) + 1


def download_file(request_context, link, dest):
    """Download a single file using Playwright’s request context."""
    try:
        resp = request_context.get(link)
        if resp.ok:
            with open(dest, "wb") as f:
                f.write(resp.body())
            return True
        else:
            print(f"❌ HTTP {resp.status} for {link}")
            return False
    except Exception as e:
        print(f"❌ Failed to download {link}: {e}")
        return False


def scrape_media(page, request_context, row):
    """Scrape media (images + videos) from a single tweet."""
    global img_index, vid_index

    url = str(row["posturl"]).strip().rstrip("/")
    if url in [u.strip().rstrip("/") for u in downloaded_urls]:
        print(f"⏭️ Skipping (already downloaded): {url}")
        return None

    video_links = []

    # Intercept responses for .mp4 links
    def handle_response(resp):
        if any(ext in resp.url for ext in [".mp4", ".m3u8"]):
            video_links.append(resp.url)

    page.on("response", handle_response)

    try:
        page.goto(url, timeout=60000)
        page.wait_for_timeout(7000)
        page.mouse.wheel(0, 8000)
        page.wait_for_timeout(3000)

        img_paths, vid_paths = [], []

        # --- IMAGES ---
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

        # --- VIDEOS ---
        page.wait_for_timeout(5000)
        for vurl in set(video_links):
            if ".mp4" in vurl:
                dest = os.path.join(video_dir, f"video{vid_index}.mp4")
                if download_file(request_context, vurl, dest):
                    vid_paths.append(dest)
                    vid_index += 1

        if vid_paths:
            row["video_path"] = ", ".join(vid_paths)

        if img_paths or vid_paths:
            return row
        else:
            print(f"⚠️ No media found for: {url}")
            return None

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return None


def main():
    """Main execution entrypoint."""
    print("🚀 Starting Playwright media downloader...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            request_context = context.request

            for idx, row in df.iterrows():
                try:
                    page = context.new_page()
                    print(f"➡️ {idx+1}/{len(df)} Processing {row['posturl']}")
                    result = scrape_media(page, request_context, row.copy())
                    page.close()
                    time.sleep(1)

                    if result is not None and isinstance(result, pd.Series):
                        new_rows.append(result)
                except Exception as e:
                    print(f"⚠️ Error row {idx}: {e}")
                    continue

            # Clean close
            context.close()
            browser.close()
            print("✅ Browser closed cleanly.")

        # Write results
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

    except Exception as e:
        print(f"❌ Critical error: {e}")


if __name__ == "__main__":
    main()
