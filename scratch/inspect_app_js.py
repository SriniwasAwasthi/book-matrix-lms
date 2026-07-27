with open('frontend/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

print("File size:", len(text))
print("Contains 'chat':", 'chat' in text.lower())
print("Contains 'initNotifications':", 'initnotifications' in text.lower())
print("Contains 'toggleTheme':", 'toggletheme' in text.lower())

import re
lines = text.split('\n')
for i, line in enumerate(lines):
    if 'action=chat' in line or 'initNotifications' in line or 'theme' in line.lower() or 'bell' in line.lower():
        print(f"{i+1}: {line.strip()[:120]}")
