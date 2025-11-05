# streamlit_app.py
import streamlit as st
import asyncio
from pathlib import Path
from (model)run_pipeline import graph_app, LLMState

st.set_page_config(page_title="Video → Twitter Action", layout="wide")
st.title("📹 Video to Twitter Action Pipeline")

# 1️⃣ Upload video
uploaded_file = st.file_uploader("Upload a video to analyze", type=["mp4", "mov", "avi"])

# 2️⃣ Optional: user can preview video
if uploaded_file is not None:
    video_path = Path("temp_uploaded_video.mp4")
    with open(video_path, "wb") as f:
        f.write(uploaded_file.read())
    
    st.video(str(video_path))

    # 3️⃣ Run pipeline button
    if st.button("▶ Run Pipeline"):
        st.info("Pipeline started... This may take a few seconds depending on video length and agent tasks.")

        # ✅ Async wrapper for Streamlit
        async def run_pipeline():
            initial_state = LLMState(
                input_video=str(video_path),
                matched_row=None,
                tweet_url="",
                complaint="",
                comment_text="",
                community_note=""
            )
            result = await graph_app.ainvoke(initial_state)
            return result

        # Run the async function in Streamlit
        try:
            result = asyncio.run(run_pipeline())
            st.success("✅ Pipeline finished!")
            st.subheader("📌 Results:")
            st.json(result)

            # Optionally, show matched tweet URL separately
            tweet_url = result.get("tweet_url")
            if tweet_url:
                st.markdown(f"**Matched Tweet URL:** [{tweet_url}]({tweet_url})")

            # Show comment text / complaint if generated
            comment_text = result.get("comment_text", "")
            complaint = result.get("complaint", "")
            if comment_text:
                st.markdown(f"**Comment Text Generated:** {comment_text}")
            if complaint:
                st.markdown(f"**Complaint:** {complaint}")

        except Exception as e:
            st.error(f"❌ Pipeline failed: {e}")


