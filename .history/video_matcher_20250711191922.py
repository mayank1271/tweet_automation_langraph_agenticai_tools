import cv2
import os
import pandas as pd
import numpy as np

# --- CONFIG ---
DATABASE_EXCEL = "final_metadata.xlsx"
VIDEO_DIR = "railways/videos"

# --- Frame Extraction Helper ---
def extract_key_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []
    duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
    timestamps = [duration / 2, duration / 4, duration / 8]
    frames = []
    for t in timestamps:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
    cap.release()
    return frames

# --- Frame Similarity ---
def frame_similarity(f1, f2):
    try:
        f1 = cv2.resize(f1, (128, 128))
        f2 = cv2.resize(f2, (128, 128))
        diff = np.abs(f1.astype("int") - f2.astype("int"))
        score = 1 - (np.mean(diff) / 255)
        return score  # closer to 1 = more similar
    except:
        return 0

# --- Core Matching Logic ---
def match_video_to_tweet(input_video_path):
    if not os.path.exists(input_video_path):
        print(f"❌ Video not found: {input_video_path}")
        return None

    if not os.path.exists(DATABASE_EXCEL):
        print(f"❌ Excel file not found: {DATABASE_EXCEL}")
        return None

    df = pd.read_excel(DATABASE_EXCEL)
    input_frames = extract_key_frames(input_video_path)

    best_match = None
    best_score = 0

    for idx, row in df.iterrows():
        video_paths = str(row.get("video_path", "")).split(", ")
        for db_video in video_paths:
            if not os.path.exists(db_video):
                continue
            db_frames = extract_key_frames(db_video)
            sim_scores = []
            for inf, dbf in zip(input_frames, db_frames):
                sim_scores.append(frame_similarity(inf, dbf))
            if sim_scores:
                avg_score = sum(sim_scores) / len(sim_scores)
                if avg_score > best_score:
                    best_score = avg_score
                    best_match = row

    if best_match is not None:
        print("\n✅ Matched Tweet Metadata (Score: {:.2f})\n".format(best_score))
        print("Post URL:", best_match.get("posturl"))
        print("Author:", best_match.get("author"))
        print("Content Text:", best_match.get("content_text"))
        print("Hashtags:", best_match.get("hashtag"))
        print("Likes Count:", best_match.get("likescount"))
        print("Comments Count:", best_match.get("commentscount"))
        print("Share Count:", best_match.get("sharecounts"))
        print("Views Count:", best_match.get("viewscount"))
        return best_match

    else:
        print("❌ No matching tweet found.")
        return None

# --- Optional: Direct test ---
if __name__ == "__main__":
    test_video = r"C:\Users\mayank manjhi\Dropbox\lang,rag,ai\railways\videos\video2.mp4"
    match_video_to_tweet(test_video)
