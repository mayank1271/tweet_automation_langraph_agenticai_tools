# (model)run_pipeline.py
from video_matcher import match_video_to_tweet
from llm_model import run_llm_decision
from agent_controller import app   # ✅ ab app import karna hai, perform_actions nahi

INPUT_VIDEO = r"C:\Users\mayank manjhi\Dropbox\lang,rag,ai\railways\videos\video25.mp4" 

def main():
    matched_row = match_video_to_tweet(INPUT_VIDEO)

    if matched_row is not None and not matched_row.empty:
        tweet_url = matched_row.get("posturl", "")
        llm_response = run_llm_decision(matched_row)  # agar ye async hai to await/ainvoke use karna padega

        if llm_response:
            state = {
                "tweet_url": tweet_url,
                "complaint": llm_response.get("complaint", ""),
                "comment_text": llm_response.get("comment_text", ""),
                "community_note": llm_response.get("community_note", "")
            }

            result = app.invoke(state)   # ✅ LangGraph se run hoga
            print("✅ Graph finished:", result)
        else:
            print("❌ LLM didn't return a valid response.")
    else:
        print("❌ Koi match nahi mila, LLM ko bhejne ka koi fayda nahi.")

if __name__ == "__main__":
    main()
