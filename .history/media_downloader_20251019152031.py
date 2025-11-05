import os
import time
import pandas as pd
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests

# --- CONFIG ---
image_dir = "railways/images"
video_dir = "railways/videos"
os.makedirs(image_dir, exist_ok=True)
os.makedirs(video_dir, exist_ok=True)

metadata_file = "mentions_output.xlsx"
final_meta_file = "final_metadata.xlsx"

df = pd.read_excel(metadata_file)
downloaded_urls = set()
if os.path.exists(final_meta_file):
    downloaded_urls = set(pd.read_excel(final_meta_file)["posturl"].astype(str).tolist())

new_rows = []

# 🛠 Dynamically continue naming from last index
existing_images = [f for f in os.listdir(image_dir) if f.startswith("image") and f.endswith(".jpg")]
existing_videos = [f for f in os.listdir(video_dir) if f.startswith("video") and f.endswith(".mp4")]

img_index = max([int(f.replace("image", "").replace(".jpg", "")) for f in existing_images] or [0]) + 1
vid_index = max([int(f.replace("video", "").replace(".mp4", "")) for f in existing_videos] or [0]) + 1


def download_file(url, dest):
    try:
        r = requests.get(url, stream=True, timeout=20)
        if r.status_code == 200:
            with open(dest, "wb") as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            return True
        else:
            print(f"❌ HTTP error {r.status_code} for {url}")
            return False
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return False


def scrape_media(driver, row):
    global img_index, vid_index
    url = str(row["posturl"]).strip().rstrip("/")
    if url in [u.strip().rstrip("/") for u in downloaded_urls]:
        return None

    try:
        driver.get(url)
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        img_paths = []
        vid_paths = []

        # --- Images ---
        imgs = driver.find_elements(By.CSS_SELECTOR, "img[src*='pbs.twimg.com/media']")
        for img in imgs:
            src = img.get_attribute("src")
            if not src or "profile_images" in src:
                continue
            dest = os.path.join(image_dir, f"image{img_index}.jpg")
            if download_file(src, dest):
                img_paths.append(dest)
                img_index += 1

        if img_paths:
            row["img_path"] = ", ".join(img_paths)

        # --- Videos ---
        # Video URLs may be embedded in <video> or <source>
        videos = driver.find_elements(By.CSS_SELECTOR, "video source")
        for v in videos:
            src = v.get_attribute("src")
            if src and ".mp4" in src:
                dest = os.path.join(video_dir, f"video{vid_index}.mp4")
                if download_file(src, dest):
                    vid_paths.append(dest)
                    vid_index += 1

        if vid_paths:
            row["video_path"] = ", ".join(vid_paths)

        return row

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return None

def main():
    driver = webdriver.Chrome()
    for _, row in tqdm(df.iterrows(), total=len(df)):
        result = scrape_media(driver, row.copy())
        if result is not None:
            new_rows.append(result)

    driver.quit()

    if new_rows:
        new_df = pd.DataFrame(new_rows)
        if os.path.exists(final_meta_file):
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
