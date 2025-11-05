# llm_model.py
import ollama
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

⚠️ Important Formatting Rule:
- Write exactly "Complaint: Yes" or "Complaint: No" (no **, no quotes, no punctuation).
- Keep output clean and consistent.

Give your answer in this format:
Complaint: Yes/No  
Action: ...  
Reason: ...  
Comment_Text: ...

Metadata:
{metadata_text}
"""


def clean_comment_text(text):
    """Removes all special characters, leaving only words and spaces."""
    cleaned = re.sub(r"[^A-Za-z0-9\s]", "", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def normalize_complaint(value: str):
    """Cleans the complaint field to just 'Yes' or 'No'."""
    if not value:
        return "No"
    val = value.strip().lower()
    if "yes" in val:
        return "Yes"
    return "No"


def parse_llm_response(text):
    parsed = {}
    pattern = re.compile(r"\*{0,2}([\w\s]+)\*{0,2}:\s*(.*)")

    lines = text.strip().splitlines()
    buffer_key = None

    for line in lines:
        match = pattern.match(line)
        if match:
            key = match.group(1).strip().lower().replace(" ", "_")
            val = match.group(2).strip().strip('"')
            parsed[key] = val
            buffer_key = key
        elif buffer_key:
            parsed[buffer_key] += " " + line.strip()

    # Default comment if missing
    if "comment_text" not in parsed:
        parsed["comment_text"] = "No comment generated"

    # ✅ Clean fields
    if "comment_text" in parsed:
        parsed["comment_text"] = clean_comment_text(parsed["comment_text"])

    if "complaint" in parsed:
        parsed["complaint"] = normalize_complaint(parsed["complaint"])

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
        print("✅ LLM Decision:\n", content)
        result = parse_llm_response(content)
        print("\n🎯 Parsed:", result)
        return result
    except Exception as e:
        print(f"❌ Ollama Error: {e}")
        return None
