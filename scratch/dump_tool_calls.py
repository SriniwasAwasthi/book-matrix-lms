import json
import os

log_file = r"C:\Users\sriaw\.gemini\antigravity-ide\brain\ba7b725d-56d7-4bd5-82d4-b4fd94ad85fe\.system_generated\logs\transcript.jsonl"

if os.path.exists(log_file):
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            if "app.js" in line or "server.py" in line:
                data = json.loads(line)
                print(f"Step: {data.get('step_index')} Type: {data.get('type')}")
                if "tool_calls" in data:
                    for tc in data["tool_calls"]:
                        print(f"  Tool name: {tc.get('name') or tc.get('ToolName')}")
                        args = tc.get("args") or tc.get("Arguments") or {}
                        print(f"  Args: {list(args.keys())}")
                        # print some of the content
                        for k, v in args.items():
                            if "content" in k.lower() or "replacement" in k.lower():
                                print(f"    {k}: {str(v)[:200]}...")
