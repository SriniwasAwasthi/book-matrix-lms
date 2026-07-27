import os
import re

frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')

count = 0
for filename in os.listdir(frontend_dir):
    if filename.endswith('.html'):
        file_path = os.path.join(frontend_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Match style.css (with or without query string)
        new_content, sub_css = re.subn(
            r'href=["\']style\.css(?:\?v=[a-zA-Z0-9_]*)?["\']', 
            'href="style.css?v=20260531_edge_fixed"', 
            content
        )
        
        # Match app.js (with or without query string)
        new_content, sub_js = re.subn(
            r'src=["\']app\.js(?:\?v=[a-zA-Z0-9_]*)?["\']', 
            'src="app.js?v=20260531_edge_fixed"', 
            new_content
        )
        
        # Match theme.js (with or without query string)
        new_content, sub_theme = re.subn(
            r'src=["\']theme\.js(?:\?v=[a-zA-Z0-9_]*)?["\']', 
            'src="theme.js?v=20260531_edge_fixed"', 
            new_content
        )
        
        if sub_css > 0 or sub_js > 0 or sub_theme > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Busted cache in {filename} (CSS: {sub_css}, JS: {sub_js}, Theme: {sub_theme})")
            count += 1

print(f"Bust cache complete. Processed {count} HTML files.")
