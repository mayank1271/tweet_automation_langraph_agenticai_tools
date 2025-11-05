# tools/utils.py
import json
from pathlib import Path

COOKIE_FILE = Path("twitter_cookies.json")

async def apply_saved_cookies(context):
    cookies = json.load(COOKIE_FILE.open())
    await context.add_cookies(cookies)
