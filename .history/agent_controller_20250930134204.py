# agent_controller.py
from typing import TypedDict
from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
from langgraph.constants import START, END  # ✅ START/END constants

# 1️⃣ Define the state schema for the agent
# TypedDict defines structure of the state that flows through the graph
class AgentState(TypedDict):
    tweet_url: str
    complaint: str
    comment_text: str
    community_note: str

# 2️⃣ Initialize workflow with the schema
workflow = StateGraph(AgentState)

# 3️⃣ Define your nodes as RunnableLambda (wrappers around async functions)

# Report node: runs when complaint == "yes"
async def report_node(state: AgentState):
    from agenticai.tools.report import report_tweet
    from agenticai.logger import record_action
    await report_tweet(state["tweet_url"])  # report the tweet
    if state.get("community_note"):
        record_action(state["tweet_url"], state["community_note"])  # log the community note
    return state  # return updated state for next node

# Like node: runs when complaint != "yes"
async def like_node(state: AgentState):
    from agenticai.tools.like import like_tweet
    await like_tweet(state["tweet_url"])  # like the tweet
    return state

# Repost node: always after like
async def repost_node(state: AgentState):
    from agenticai.tools.repost import repost_tweet
    await repost_tweet(state["tweet_url"])  # repost the tweet
    return state

# Comment node: runs if comment_text exists
async def comment_node(state: AgentState):
    from agenticai.tools.comment import comment_tweet
    if state.get("comment_text"):
        await comment_tweet(state["tweet_url"], state["comment_text"])  # comment
    return state

# 4️⃣ Add nodes to workflow
workflow.add_node("report", RunnableLambda(report_node))
workflow.add_node("like", RunnableLambda(like_node))
workflow.add_node("repost", RunnableLambda(repost_node))
workflow.add_node("comment", RunnableLambda(comment_node))

# 5️⃣ Define conditional edges
# Conditional edge from START based on complaint
def start_condition(state: AgentState):
    # ✅ Decide next node based on complaint
    if state["complaint"].lower() == "yes":
        return "report"
    else:
        return "like"

workflow.add_conditional_edges(
    START,  # use START constant, not "start"
    start_condition,
    {
        "report": "report",
        "like": "like",
    }
)

# 6️⃣ Normal edges (sequence nodes)
workflow.add_edge("like", "repost")       # after liking, repost
workflow.add_edge("repost", "comment")    # after reposting, check comment
workflow.add_edge("report", END)          # after reporting, go to END
workflow.add_edge("comment", END)         # after commenting (or skipping), go to END

# 7️⃣ Compile the workflow to an app object
# ✅ This app can now be invoked to run the graph
app = workflow.compile()
