import os
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

logs_dir = r"C:\Users\sriaw\.gemini\antigravity-ide\brain"
conv = "f0cca2b9-4b88-4e32-b66c-fb4825d78c82"
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
                    print(f"\n[{sindex}] USER:\n{content}")
                elif stype == "PLANNER_RESPONSE" or stype == "MODEL":
                    if content:
                        print(f"\n[{sindex}] AGENT:\n{content}")
    except Exception as e:
        print(f"Error reading {conv}: {e}")
else:
    print(f"File not found: {log_file}")
