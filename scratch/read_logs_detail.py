import json
import os

logs_dir = r"C:\Users\sriaw\.gemini\antigravity-ide\brain"
conv = "ba7b725d-56d7-4bd5-82d4-b4fd94ad85fe"
log_file = os.path.join(logs_dir, conv, ".system_generated", "logs", "transcript.jsonl")

if os.path.exists(log_file):
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            tool_calls = data.get("tool_calls", [])
            for tc in tool_calls:
                name = tc.get("ToolName", "")
                if "replace_file_content" in name or "write_to_file" in name:
                    args = tc.get("Arguments", {})
                    target = args.get("TargetFile", args.get("Target", ""))
                    if "app.js" in target or "server.py" in target:
                        print(f"Tool: {name} on {target}")
                        print(f"Instruction: {args.get('Instruction')}")
                        print(f"ReplacementContent:\n{args.get('ReplacementContent')}\n")
                        print("-" * 50)
