import pandas as pd
import os

def record_action(url, action, note):
    path = "action_log.xlsx"
    row = {"url": url, "action": action, "note": note}
    if os.path.exists(path):
        df = pd.read_excel(path)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])
    df.to_excel(path, index=False)
    print(f"✅ Action recorded: {action} → {url}")
