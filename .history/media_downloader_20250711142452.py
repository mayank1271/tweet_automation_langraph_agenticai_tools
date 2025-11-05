import os
import asyncio
import pandas as pd
from tqdm.asyncio import tqdm
from playwright.async_api import async_playwright

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

# Get max existing index to avoid overwrite
img_index = max([int(f.replace("image", "").replace(".jpg", "")) for f in existing_images] or [0]) + 1
vid_index = max([int(f.replace("video", "").replace(".mp4", "")) for f in existing_videos] or [0]) + 1


async def download_file(request_context, link, dest):
    try:
        resp = await request_context.get(link)
        if resp.ok:
            with open(dest, "wb") as f:
                f.write(await resp.body())
            return True
        else:
            print(f"❌ HTTP Error {resp.status} for {link}")
            return False
    except Exception as e:
        print(f"❌ Failed to download {link}: {e}")
        return False

async def scrape_media(browser_context, request_context, row):
    global img_index, vid_index
    url = str(row["posturl"]).strip().rstrip("/")
    if url in [u.strip().rstrip("/") for u in downloaded_urls]:
        return None

    tweet_id = url.strip("/").split("/")[-1]
    username = url.strip("/").split("/")[-3]
    tweet_url = f"https://x.com/{username}/status/{tweet_id}"

    try:
        page = await browser_context.new_page()
        video_links = []

        # 🟢 Intercept responses and sniff video links
        page.on("response", lambda resp: video_links.append(resp.url) if (".mp4" in resp.url or ".m3u8" in resp.url) else None)

        await page.goto(tweet_url, timeout=60000)
        await page.wait_for_timeout(7000)
        await page.mouse.wheel(0, 8000)
        await page.wait_for_timeout(3000)

        img_paths = []
        vid_paths = []

        # --- Images ---
        imgs = await page.query_selector_all("img[src*='pbs.twimg.com/media']")
        for img in imgs:
            src = await img.get_attribute("src")
            if not src or "profile_images" in src:
                continue
            dest = os.path.join(image_dir, f"image{img_index}.jpg")
            success = await download_file(request_context, src, dest)
            if success:
                img_paths.append(dest)
                img_index += 1

        if img_paths:
            row["img_path"] = ", ".join(img_paths)

        # --- Videos ---
        await page.wait_for_timeout(5000)
        video_links = list(set(video_links))

        for vurl in video_links:
            if ".mp4" in vurl:
                dest = os.path.join(video_dir, f"video{vid_index}.mp4")
                success = await download_file(request_context, vurl, dest)
                if success:
                    vid_paths.append(dest)
                    vid_index += 1

        if vid_paths:
            row["video_path"] = ", ".join(vid_paths)

        await page.close()
        return row  # ✅ Important: return updated row

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return None

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        request_context = await p.request.new_context()

        for _, row in tqdm(df.iterrows(), total=len(df)):
            result = await scrape_media(context, request_context, row.copy())
            if result is not None:
                new_rows.append(result)

        await browser.close()
        await request_context.dispose()

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
    asyncio.run(main())


