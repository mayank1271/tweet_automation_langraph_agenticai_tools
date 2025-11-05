# run_pipeline.py
from agent_controller import app  # LangGraph compiled workflow for agent actions
from video_matcher import match_video_to_tweet
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph
from langgraph.constants import START, END
from typing import TypedDict
import asyncio

# ✅ Define state for the pre-agent workflow
class LLMState(TypedDict):
    input_video: str
    matched_row: dict
    tweet_url: str
    complaint: str
    comment_text: str

# Video file path
INPUT_VIDEO = r"C:\Users\mayank manjhi\Downloads\(1)lang,rag,ai\railways\videos\video82.mp4"

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

    return state

# 3️⃣ Build workflow including match + LLM + agent_controller
workflow = StateGraph(LLMState)

workflow.add_node("match", RunnableLambda(match_node))
workflow.add_node("llm", RunnableLambda(llm_node))

# ✅ Fix here: wrap agent workflow correctly
async def agent_actions_node(state: LLMState):
    result = await app.ainvoke(state)   # Await subgraph
    return {**state, **result} 

workflow.add_node("agent_actions", RunnableLambda(agent_actions_node))

# ✅ Add START edge (entrypoint)
workflow.add_edge(START, "match")

# Sequential edges
workflow.add_edge("match", "llm")
workflow.add_edge("llm", "agent_actions")
workflow.add_edge("agent_actions", END)

# Compile the workflow
graph_app = workflow.compile()

# 4️⃣ Run the pipeline
def main():
    # ✅ Make sure all keys exist in initial_state
    initial_state = {
        "input_video": INPUT_VIDEO,
        "matched_row": None,
        "tweet_url": "",
        "complaint": "",
        "comment_text": "",
       
    }
    result = asyncio.run(graph_app.ainvoke(initial_state))
    print("✅ Pipeline finished:", result)

if __name__ == "__main__":
    main()
