import json
import os

logs_dir = r"C:\Users\sriaw\.gemini\antigravity-ide\brain"
conv = "08a1de1f-3971-43d7-b057-3cd5fdc4b726"
log_file = os.path.join(logs_dir, conv, ".system_generated", "logs", "transcript.jsonl")

if os.path.exists(log_file):
    print(f"--- LOGS FOR CONVERSATION {conv} ---")
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                if data.get("type") == "USER_INPUT":
                    print(f"\n[USER]: {data.get('content')}")
                elif data.get("type") == "PLANNER_RESPONSE":
                    print(f"\n[PLANNER]: {data.get('content')}")
                elif data.get("tool_calls"):
                    for tc in data.get("tool_calls"):
                        tool_name = tc.get("ToolName")
                        if tool_name in ["replace_file_content", "write_to_file", "multi_replace_file_content"]:
                            args = tc.get("Arguments", {})
                            target = args.get("TargetFile", args.get("Target", ""))
                            print(f"[TOOL {tool_name}]: {target}")
    except Exception as e:
        print(f"Error reading {conv}: {e}")
else:
    print(f"File not found: {log_file}")
