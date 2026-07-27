import os
import json

logs_dir = r"C:\Users\sriaw\.gemini\antigravity-ide\brain"
keywords = ["font", "serif", "cinzel", "playfair", "outfit", "style", "design", "appearance"]

def search_logs():
    subdirs = [d for d in os.listdir(logs_dir) if os.path.isdir(os.path.join(logs_dir, d))]
    matches = []
    for sd in subdirs:
        transcript_path = os.path.join(logs_dir, sd, ".system_generated", "logs", "transcript.jsonl")
        if os.path.exists(transcript_path):
            try:
                with open(transcript_path, "r", encoding="utf-8") as f:
                    for idx, line in enumerate(f):
                        data = json.loads(line)
                        content = data.get("content", "")
                        if not content:
                            continue
                        content_lower = content.lower()
                        for kw in keywords:
                            if kw in content_lower:
                                matches.append((sd, data.get("type"), kw, content[:150]))
                                break
            except Exception as e:
                pass
    
    print(f"Found {len(matches)} potential references in transcripts:")
    for sd, step_type, kw, snippet in matches[-20:]:  # show recent 20
        print(f"Conv: {sd} | Type: {step_type} | Keyword: {kw} | Snippet: {snippet.strip()}")

search_logs()
