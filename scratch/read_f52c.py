import os
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

logs_dir = r"C:\Users\sriaw\.gemini\antigravity-ide\brain"
conv = "f52c76cf-22a0-4a63-8b19-2d9779cc4574"
log_file = os.path.join(logs_dir, conv, ".system_generated", "logs", "transcript.jsonl")

if os.path.exists(log_file):
    print(f"--- LOGS FOR CONVERSATION {conv} ---")
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                stype = data.get("type")
                sindex = data.get("step_index")
                content = data.get("content", "")
                if stype == "USER_INPUT":
                    print(f"\n[{sindex}] USER:\n{content[:500]}")
                elif stype == "PLANNER_RESPONSE" or stype == "MODEL":
                    if content:
                        # Find write_to_file or replace_file_content in tools if any, but let's print model's response summary
                        print(f"\n[{sindex}] AGENT:\n{content[:500]}")
    except Exception as e:
        print(f"Error reading {conv}: {e}")
else:
    print(f"File not found: {log_file}")
