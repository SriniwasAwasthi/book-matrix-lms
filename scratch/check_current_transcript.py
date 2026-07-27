import json
import os

log_file = r"C:\Users\sriaw\.gemini\antigravity-ide\brain\1d466687-bb67-43c8-a451-8d6243d04bb2\.system_generated\logs\transcript.jsonl"

if os.path.exists(log_file):
    with open(log_file, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if "call_mcp" in line or "chrome-devtools" in line:
                print(f"Match on line {idx}: {line[:300]}...")
else:
    print("Current transcript not found")
