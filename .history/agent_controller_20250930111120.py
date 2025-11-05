from langgraph.graph import StateGraph

workflow = StateGraph()

# Define nodes
workflow.add_node("start")
workflow.add_node("check_complaint")
workflow.add_node("report_tweet")
workflow.add_node("record_note")
workflow.add_node("like_tweet")
workflow.add_node("repost_tweet")
workflow.add_node("check_comment")
workflow.add_node("comment_tweet")
workflow.add_node("end")

# Add edges
workflow.add_edge("start", "check_complaint")

# Complaint = yes path
workflow.add_edge("check_complaint", "report_tweet", condition=lambda s: s["complaint"]=="yes")
workflow.add_edge("report_tweet", "record_note", condition=lambda s: bool(s.get("community_note")))
workflow.add_edge("record_note", "end")
workflow.add_edge("report_tweet", "end", condition=lambda s: not s.get("community_note"))

# Complaint != yes path
workflow.add_edge("check_complaint", "like_tweet", condition=lambda s: s["complaint"]!="yes")
workflow.add_edge("like_tweet", "repost_tweet")
workflow.add_edge("repost_tweet", "check_comment")
workflow.add_edge("check_comment", "comment_tweet", condition=lambda s: bool(s.get("comment_text")))
workflow.add_edge("check_comment", "end", condition=lambda s: not s.get("comment_text"))
workflow.add_edge("comment_tweet", "end")
