# agenticai/tools/report_tool_node.py
from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
from typing import TypedDict
from playwright.async_api import async_playwright, TimeoutError
from langchain.tools import Tool

# ✅ Safe import
try:
    from .utils import apply_saved_cookies
except ImportError:
    from utils import apply_saved_cookies

# 1️⃣ Define state schema
class ReportState(TypedDict):
    tweet_url: str

# 2️⃣ Async function to report tweet
async def report_tweet_node(state: ReportState):
    tweet_url = state["tweet_url"]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        await apply_saved_cookies(context)
        page = await context.new_page()

        await page.goto(tweet_url, timeout=60000)
        await page.wait_for_timeout(3000)

        if "login" in page.url:
            print("❌ Not logged in. Cannot report tweet.")
            await browser.close()
            return state

        try:
            await page.click('div[aria-label="More"]')
            await page.get_by_text("Report Post").click()
            await page.get_by_text("It's suspicious or spam").click()
            await page.get_by_text("Next").click()
            await page.get_by_text("Submit").click()
            print(f"🚨 Reported: {tweet_url}")
        except Exception as e:
            await page.screenshot(path="report_debug.png", full_page=True)
            print(f"❌ Report failed: {e} (screenshot saved)")

        await browser.close()

    return state  # Return state for next node in graph

# 3️⃣ Wrap it as a LangGraph node
report_node = RunnableLambda(report_tweet_node)

# 4️⃣ Optional: create a LangChain Tool
report_tool = Tool.from_function(
    name="report_tweet",
    func=report_tweet_node,
    description="Report a tweet as suspicious or spam using saved cookies. Input: {'tweet_url': '<URL>'}."
)

# 5️⃣ Optional: example mini workflow
if __name__ == "__main__":
    from langgraph.constants import START, END
    workflow = StateGraph(ReportState)
    workflow.add_node("report", report_node)
    workflow.add_edge(START, "report")
    workflow.add_edge("report", END)
    app = workflow.compile()

    import asyncio
    initial_state = {"tweet_url": "https://twitter.com/example/status/123"}
    asyncio.run(app.ainvoke(initial_state))
