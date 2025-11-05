from typing import TypedDict
from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda

# 1. Define the state schema
class AgentState(TypedDict):
    tweet_url: str
    complaint: str
    comment_text: str
    community_note: str

# 2. Initialize workflow with schema
workflow = StateGraph(AgentState)

# 3. Define your nodes as RunnableLambda (wrappers around functions)
async def report_node(state: AgentState):
    from agenticai.tools.report import report_tweet
    from agenticai.logger import record_action
    await report_tweet(state["tweet_url"])
    if state.get("community_note"):
        record_action(state["tweet_url"], state["community_note"])
    return state

async def like_node(state: AgentState):
    from agenticai.tools.like import like_tweet
    await like_tweet(state["tweet_url"])
    return state

async def repost_node(state: AgentState):
    from agenticai.tools.repost import repost_tweet
    await repost_tweet(state["tweet_url"])
    return state

async def comment_node(state: AgentState):
    from agenticai.tools.comment import comment_tweet
    if state.get("comment_text"):
        await comment_tweet(state["tweet_url"], state["comment_text"])
    return state

# 4. Add nodes
workflow.add_node("report", RunnableLambda(report_node))
workflow.add_node("like", RunnableLambda(like_node))
workflow.add_node("repost", RunnableLambda(repost_node))
workflow.add_node("comment", RunnableLambda(comment_node))

# 5. Add conditional edges
workflow.add_edge("start", "report", condition=lambda s: s["complaint"].lower()=="yes")
workflow.add_edge("start", "like", condition=lambda s: s["complaint"].lower()!="yes")
workflow.add_edge("like", "repost")
workflow.add_edge("repost", "comment")
workflow.add_edge("report", "end")
workflow.add_edge("comment", "end")

# 6. Compile workflow
app = workflow.compile()
