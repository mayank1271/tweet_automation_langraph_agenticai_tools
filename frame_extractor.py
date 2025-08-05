import os
import cv2
import pytesseract
import pandas as pd
from ultralytics import YOLO
from PIL import Image

# --- CONFIG ---
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
video_dir = "railways/videos"
meta_file = "final_metadata.xlsx"
model = YOLO("yolov8n.pt")

# --- Frame Feature Extractors ---
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
            frames.append((int(t), frame))
    cap.release()
    return frames

def extract_text(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    pil_img = Image.fromarray(gray)
    return pytesseract.image_to_string(pil_img)

def detect_objects(frame):
    results = model(frame)
    return list(set([model.names[int(cls)] for cls in results[0].boxes.cls]))

# --- Load Existing Metadata ---
df = pd.read_excel(meta_file)
updated_rows = []

for idx, row in df.iterrows():
    video_paths = str(row.get("video_path", "")).split(", ")
    all_features = {}

    for vpath in video_paths:
        if not os.path.exists(vpath) or not vpath.endswith(".mp4"):
            continue
        frames = extract_key_frames(vpath)
        for j, (ts, frame) in enumerate(frames):
            text = extract_text(frame).strip()
            objects = detect_objects(frame)
            all_features[f"frame{j+1}_ts"] = ts
            all_features[f"frame{j+1}_text"] = text
            all_features[f"frame{j+1}_objects"] = ", ".join(objects)
    
    for k, v in all_features.items():
        df.at[idx, k] = v

df.to_excel(meta_file, index=False)
print(f"✅ Frame features updated in {meta_file}")
