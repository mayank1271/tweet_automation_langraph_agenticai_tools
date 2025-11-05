## Project Dependencies

Install all required libraries before running the pipeline:

```
selenium
undetected-chromedriver
webdriver-manager
playwright
pandas
openpyxl
schedule
pytz
python-dateutil
numpy
opencv-python
pytesseract
ultralytics
Pillow
langgraph
langchain-core
ollama
```

After installing Playwright, run:

```
playwright install
```

Make sure **Tesseract OCR** is installed on your machine, and the path in your code matches your installation location.

---

## Overview

This project provides an end-to-end automation pipeline for processing Twitter (X) content. The system fetches posts, downloads media, analyzes video content, matches external videos to their originating tweets, classifies sentiment using a language model, and performs actions such as reporting, liking, reposting, or commenting automatically.

Once initial setup is complete, the workflow runs without manual intervention.

---

## Chrome Login Setup (Required Before Running Pipeline)

This setup ensures Selenium attaches to a Chrome session that is already logged in, so you do not have to log in each time.

1. Install required packages:

```
pip install selenium webdriver-manager
```

2. Create a dedicated Chrome profile directory:

```
C:\SeleniumProfile
```

3. Close all running Chrome windows and start Chrome in debug mode:

For 64-bit systems:

```
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\SeleniumProfile"
```

For 32-bit systems:

```
"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\SeleniumProfile"
```

When Chrome opens, log in to X.com once. The login will remain saved.

4. Ensure your Selenium connection code references the same profile path and port.

5. You may now run the pipeline normally.

---

## Workflow Description

### 1. Tweet Fetching (tweet_fetch_uc.py)

Logs into X using the saved Chrome session and collects recent tweets from selected accounts. Extracts metadata including text, author, hashtags, views, and media links. Saves the output to `mentions_output.xlsx`.

Technologies: Selenium, Undetected ChromeDriver, Pandas.

---

### 2. Media Downloading (media_downloader.py)

Reads tweet URLs from the metadata file and uses Playwright to download associated images and videos. Media paths are linked back to tweet records and stored in `final_metadata.xlsx`.

Technologies: Playwright, Pandas.

---

### 3. Frame Extraction and Video Analysis (frame_extractor.py)

Processes each downloaded video by:

* Extracting key frames using OpenCV
* Recognizing text using Tesseract OCR
* Detecting objects using YOLOv8

All extracted information is appended to `final_metadata.xlsx`.

Technologies: OpenCV, Tesseract OCR, YOLOv8, Pandas.

---

### 4. Video Matching (video_matcher.py)

When an input video is provided, key frames are extracted and compared against stored videos using pixel similarity. The closest matching tweet is selected.

Technologies: OpenCV, NumPy.

---

### 5. Language Model Decision Layer (llm_model.py)

The matched tweet metadata is evaluated using LLaMA-3 (via Ollama). The model determines whether the post is a complaint or a positive message and generates either a community note or a positive comment.

Technologies: Ollama, Text Parsing.

---

### 6. Automated Action Execution (agent_controller.py)

Based on the model decision:

* Complaint → Report is triggered
* Positive → Like, Repost, and Comment are performed automatically

Technologies: LangGraph, Agent Controller.

---

### 7. Pipeline Orchestration (run_pipeline.py)

This script manages the full pipeline:

1. Accepts an input video
2. Matches the video to a stored tweet
3. Sends metadata to the LLM
4. Invokes the agent to perform the appropriate action

Only the input video needs to be provided. All other steps execute automatically.

---

## Running the System

After Chrome login setup is complete, run:

```
python run_pipeline.py
```

Update the input video path inside the script as needed.

---

## Summary

This system:

* Monitors social media content
* Downloads and processes visual media
* Matches videos to their source posts
* Classifies tweet intent using a language model
* Performs automated engagement or reporting actions

It is a fully autonomous pipeline integrating computer vision, language understanding, and action automation.
