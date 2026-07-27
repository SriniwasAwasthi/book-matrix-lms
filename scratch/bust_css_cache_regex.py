import os
import re

frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')

count = 0
for filename in os.listdir(frontend_dir):
    if filename.endswith('.html'):
        file_path = os.path.join(frontend_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Regex to match href="style.css..." or href='style.css...'
        new_content, sub_count_css = re.subn(r'href=["\']style\.css(?:\?v=[a-zA-Z0-9_]*)?["\']', 'href="style.css?v=20260531"', content)
        # Regex to match src="app.js..." or src='app.js...'
        new_content, sub_count_js = re.subn(r'src=["\']app\.js(?:\?v=[a-zA-Z0-9_]*)?["\']', 'src="app.js?v=20260531"', new_content)
        
        if sub_count_css > 0 or sub_count_js > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Busted cache in {filename} (CSS: {sub_count_css}, JS: {sub_count_js})")
            count += 1

print(f"Processed {count} HTML files.")
