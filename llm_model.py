# llm_model.py
import ollama
import pandas as pd
import re

model_name = "llama3"

metadata_fields = [
    "posturl", "author", "content_text", "hashtag",
    "likescount", "commentscount", "sharecounts", "viewscount"
]

def get_metadata_table(row):
    table = ""
    for field in metadata_fields:
        val = str(row.get(field, "")).strip()
        table += f"{field.replace('_', ' ').title()}: {val}\n"
    return table

def build_prompt(metadata_text):
    return f"""
Below is a tweet post's metadata. You are an AI judge that decides whether the post is a complaint or appreciation. Based on the content:

1. Decide if it's a complaint (Yes/No)
2. If Yes, give action: Report
   - Also write a short community note (max 25 words)
3. If No, give action: Like, Repost, Comment
   - Also write a positive comment (max 25 words)

Give your answer in **tabular format** like:
Complaint: Yes/No  
Action: ...  
Reason: ...  
Community_Note: ...  
Comment_Text: ...

Metadata:
{metadata_text}
"""

def parse_llm_response(text):
    parsed = {}
    # Regex to match "**Key:** Value" OR "Key: Value"
    pattern = re.compile(r"\*{0,2}([\w\s]+)\*{0,2}:\s*(.+)")

    for line in text.strip().splitlines():
        match = pattern.match(line)
        if match:
            key = match.group(1).strip().lower().replace(" ", "_")
            val = match.group(2).strip().strip('"')
            parsed[key] = val
    return parsed

async def run_llm_decision(row):
    metadata_text = get_metadata_table(row)
    prompt = build_prompt(metadata_text)

    print("\n🤖 Sending to Ollama...\n")
    try:
        response = ollama.chat(model=model_name, messages=[
            {"role": "user", "content": prompt}
        ])
        content = response['message']['content']
        print("✅ LLM Decision:\n")
        print(content)
        return parse_llm_response(content)
    except Exception as e:
        print(f"❌ Ollama Error: {e}")
        return None
