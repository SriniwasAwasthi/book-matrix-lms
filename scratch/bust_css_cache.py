import os

frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')

count = 0
for filename in os.listdir(frontend_dir):
    if filename.endswith('.html'):
        file_path = os.path.join(frontend_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        updated = False
        if 'href="style.css"' in content:
            content = content.replace('href="style.css"', 'href="style.css?v=20260531"')
            updated = True
        elif "href='style.css'" in content:
            content = content.replace("href='style.css'", "href='style.css?v=20260531'")
            updated = True
            
        # Let's also do cache busting for app.js if it doesn't have it or has old version
        if 'src="app.js"' in content:
            content = content.replace('src="app.js"', 'src="app.js?v=20260531"')
            updated = True
        elif 'src="app.js?v=20260529"' in content:
            content = content.replace('src="app.js?v=20260529"', 'src="app.js?v=20260531"')
            updated = True
            
        if updated:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Busted cache in {filename}")
            count += 1

print(f"Processed {count} HTML files.")
