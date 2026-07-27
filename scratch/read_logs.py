import json
import os

logs_dir = r"C:\Users\sriaw\.gemini\antigravity-ide\brain"
conversations = ["9d2331d6-fc03-48e9-8283-7f0e9847bc4b", "ba7b725d-56d7-4bd5-82d4-b4fd94ad85fe", "08e2ed45-bde3-425b-8a00-87e7e9d1ff31"]

for conv in conversations:
    log_file = os.path.join(logs_dir, conv, ".system_generated", "logs", "transcript.jsonl")
    if os.path.exists(log_file):
        print(f"--- LOGS FOR CONVERSATION {conv} ---")
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line)
                    if data.get("type") == "USER_INPUT":
                        print(f"USER: {data.get('content')}")
                    elif data.get("tool_calls"):
                        for tc in data.get("tool_calls"):
                            if "replace_file_content" in tc.get("ToolName", "") or "write_to_file" in tc.get("ToolName", ""):
                                args = tc.get("Arguments", {})
                                target = args.get("TargetFile", args.get("Target", ""))
                                if "app.js" in target or "server.py" in target or "messages.html" in target:
                                    print(f"TOOL {tc.get('ToolName')}: {target}")
        except Exception as e:
            print(f"Error reading {conv}: {e}")
