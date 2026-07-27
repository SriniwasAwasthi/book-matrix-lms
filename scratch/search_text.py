import os

def search_text(query, folder="."):
    query = query.lower()
    for root, dirs, files in os.walk(folder):
        if ".git" in root or ".system_generated" in root:
            continue
        for file in files:
            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, 1):
                        if query in line.lower():
                            print(f"{filepath}:{i}: {line.strip()}")
            except Exception as e:
                pass

if __name__ == "__main__":
    import sys
    query = "error"
    if len(sys.argv) > 1:
        query = sys.argv[1]
    print(f"Searching for: '{query}'")
    search_text(query)
