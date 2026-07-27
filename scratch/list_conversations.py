import os
import json

logs_dir = r"C:\Users\sriaw\.gemini\antigravity-ide\brain"
if os.path.exists(logs_dir):
    subdirs = [d for d in os.listdir(logs_dir) if os.path.isdir(os.path.join(logs_dir, d))]
    print(f"Found {len(subdirs)} conversation directories:")
    for sd in subdirs:
        # try to read metadata or plan or summaries
        meta_path = os.path.join(logs_dir, sd, "metadata.json")
        summary_info = ""
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    summary_info = meta.get("summary", "")
            except:
                pass
        
        # also read the first line of the transcript if possible
        transcript_path = os.path.join(logs_dir, sd, ".system_generated", "logs", "transcript.jsonl")
        first_user_request = ""
        if os.path.exists(transcript_path):
            try:
                with open(transcript_path, "r", encoding="utf-8") as f:
                    for line in f:
                        data = json.loads(line)
                        if data.get("type") == "USER_INPUT":
                            first_user_request = data.get("content", "")[:100]
                            break
            except:
                pass
        
        print(f"ID: {sd} | First Input: {first_user_request}")
else:
    print(f"Logs directory not found at {logs_dir}")
