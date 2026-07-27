import json
import os

log_file = r"C:\Users\sriaw\.gemini\antigravity-ide\brain\ba7b725d-56d7-4bd5-82d4-b4fd94ad85fe\.system_generated\logs\transcript.jsonl"

if os.path.exists(log_file):
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            if data.get("step_index") == 80:
                tc = data["tool_calls"][0]
                args = tc.get("args") or {}
                print("TARGET CONTENT:")
                print(args.get("TargetContent"))
                print("="*40)
                print("REPLACEMENT CONTENT:")
                print(args.get("ReplacementContent"))
