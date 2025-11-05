# run_pipeline.py
from agent_controller import app  # LangGraph compiled workflow
from video_matcher import match_video_to_tweet
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph
from typing import TypedDict
import asyncio

# Optional: define state for LLM node if needed
class LLMState(TypedDict):
    matched_row: dict
    tweet_url: str
    complaint: str
    comment_text: str
    community_note: str

INPUT_VIDEO = r"C:\Users\mayank manjhi\Dropbox\lang,rag,ai\railways\videos\video25.mp4"

# 1️⃣ Match video node
async def match_node(state: LLMState):
    matched_row = match_video_to_tweet(state["input_video"])
    state["matched_row"] = matched_row
    if matched_row is not None and not matched_row.empty:
        state["tweet_url"] = matched_row.get("posturl", "")
    return state

# 2️⃣ LLM decision node
async def llm_node(state: LLMState):
    from llm_model import run_llm_decision
    if state.get("matched_row") is not None and not state["matched_row"].empty:
        llm_response = await run_llm_decision(state["matched_row"])
        state["complaint"] = llm_response.get("complaint", "")
        state["comment_text"] = llm_response.get("comment_text", "")
        state["community_note"] = llm_response.get("community_note", "")
    return state

# 3️⃣ Build a mini workflow to include match + LLM before agent_controller app
workflow = StateGraph(LLMState)

workflow.add_node("match", RunnableLambda(match_node))
workflow.add_node("llm", RunnableLambda(llm_node))
workflow.add_node("agent_actions", RunnableLambda(lambda state: app.ainvoke(state)))  # nested invoke

# Normal sequential edges
workflow.add_edge("match", "llm")
workflow.add_edge("llm", "agent_actions")

# Compile the workflow
graph_app = workflow.compile()

# 4️⃣ Run the pipeline
def main():
    initial_state = {"input_video": INPUT_VIDEO}
    result = asyncio.run(graph_app.ainvoke(initial_state))  # graph handles async nodes
    print("✅ Pipeline finished:", result)

if __name__ == "__main__":
    main()
