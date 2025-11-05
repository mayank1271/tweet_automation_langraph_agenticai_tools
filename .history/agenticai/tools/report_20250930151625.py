# tools/report_tool_node.py
from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
from typing import TypedDict
from playwright.async_api import async_playwright
from agenticai.tools.utils import apply_saved_cookies

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

        try:
            await page.click('div[aria-label="More"]')
            await page.get_by_text("Report Post").click()
            await page.get_by_text("It's suspicious or spam").click()
            await page.get_by_text("Next").click()
            await page.get_by_text("Submit").click()
            print(f"🚨 Reported: {tweet_url}")
        except Exception as e:
            print(f"❌ Report failed: {e}")

        await browser.close()

    return state  # return state for next node in graph

# 3️⃣ Wrap it as a LangGraph node
report_node = RunnableLambda(report_tweet_node)

# 4️⃣ Optional: example of using it in a mini workflow
if __name__ == "__main__":
    from langgraph.graph import StateGraph
    from langgraph.constants import START, END
    workflow = StateGraph(ReportState)
    workflow.add_node("report", report_node)
    workflow.add_edge(START, "report")
    workflow.add_edge("report", END)
    app = workflow.compile()

    import asyncio
    initial_state = {"tweet_url": "https://twitter.com/example/status/123"}
    asyncio.run(app.ainvoke(initial_state))
