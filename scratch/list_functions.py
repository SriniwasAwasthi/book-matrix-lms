import re

with open('frontend/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Match function statements
funcs = re.findall(r'function\s+(\w+)\s*\(|const\s+(\w+)\s*=\s*\([^)]*\)\s*=>|async\s+function\s+(\w+)\s*\(', text)
print("Functions in app.js:")
for f in funcs:
    name = next(x for x in f if x)
    print("- " + name)
