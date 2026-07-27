import json
import os

log_file = r"C:\Users\sriaw\.gemini\antigravity-ide\brain\1d466687-bb67-43c8-a451-8d6243d04bb2\.system_generated\logs\transcript.jsonl"

if os.path.exists(log_file):
    with open(log_file, "r", encoding="utf-8") as f:
        for idx in range(15):
            line = f.readline()
            if not line:
                break
            data = json.loads(line)
            print(f"Step {idx}: Source={data.get('source')} Type={data.get('type')} Status={data.get('status')} ContentLen={len(data.get('content', '')) if data.get('content') else 0}")
            if "tool_calls" in data:
                print(f"  Tool Calls: {[tc.get('name') for tc in data['tool_calls']]}")
else:
    print("Log file not found")
