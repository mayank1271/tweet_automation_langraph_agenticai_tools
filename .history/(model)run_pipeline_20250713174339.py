# (model)run_pipeline.py
from video_matcher import match_video_to_tweet
from llm_model import run_llm_decision
from agent_controller import perform_actions
import asyncio

INPUT_VIDEO = "railways/videos/video2.mp4"

async def main():
    matched_row = match_video_to_tweet(INPUT_VIDEO)

    if matched_row is not None and not matched_row.empty:
        tweet_url = matched_row.get("posturl", "")
        llm_response = await run_llm_decision(matched_row)

        if llm_response:
            await perform_actions(tweet_url, llm_response)
        else:
            print("❌ LLM didn't return a valid response.")
    else:
        print("❌ Koi match nahi mila, LLM ko bhejne ka koi fayda nahi.")

if __name__ == "__main__":
    asyncio.run(main())
