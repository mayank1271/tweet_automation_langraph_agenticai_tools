# agent_controller.py
from agenticai.tools.like import like_tweet
from agenticai.tools.comment import comment_tweet
from agenticai.tools.repost import repost_tweet
from agenticai.tools.report import report_tweet
from agenticai.logger import record_action

async def perform_actions(tweet_url, parsed):
    complaint = parsed.get("complaint", "").lower()
    action = parsed.get("action", "").lower()
    comment = parsed.get("comment_text", "")
    note = parsed.get("community_note", "")

    if complaint == "yes":
        await report_tweet(tweet_url)
        if note:
            record_action(tweet_url, note)
    else:
        await like_tweet(tweet_url)
        await repost_tweet(tweet_url)
        if comment:
            print(f"📝 Commenting with text: {comment}")
            await comment_tweet(tweet_url, comment)
        else:
            print("No comment text provided.")


