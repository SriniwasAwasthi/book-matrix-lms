import os
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

logs_dir = r"C:\Users\sriaw\.gemini\antigravity-ide\brain"
subdirs = [d for d in os.listdir(logs_dir) if os.path.isdir(os.path.join(logs_dir, d))]

for sd in subdirs:
    transcript_path = os.path.join(logs_dir, sd, ".system_generated", "logs", "transcript.jsonl")
    if os.path.exists(transcript_path):
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                first_line = f.readline()
                if not first_line:
                    continue
                data = json.loads(first_line)
                content = data.get("content", "")
                # We filter by keywords related to the library system database or book matrix to identify relevant conversations
                if any(x in content.lower() for x in ["library", "book", "member", "borrow", "dbms", "libraria", "matrix"]):
                    print(f"\n--- CONVERSATION {sd} ---")
                    print(f"USER: {content[:300]}")
                    
                    # Print all other user requests in this conversation
                    f.seek(0)
                    for line in f:
                        step = json.loads(line)
                        if step.get("type") == "USER_INPUT" and step.get("content") != content:
                            print(f"USER (follow-up): {step.get('content')[:300]}")
        except Exception as e:
            pass
