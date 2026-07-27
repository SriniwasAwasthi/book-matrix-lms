import os

def inject_theme_script():
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
    print(f"Scanning HTML files in: {frontend_dir}")
    
    script_tag = '<script src="theme.js"></script>\n'
    
    for filename in os.listdir(frontend_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(frontend_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Idempotency check: if theme.js is already injected, skip
            if 'theme.js' in content:
                print(f"Skipping {filename}: already has theme.js script.")
                continue
                
            if '<head>' in content:
                parts = content.split('<head>', 1)
                new_content = parts[0] + '<head>\n    ' + script_tag + parts[1]
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Injected theme.js into: {filename}")
            else:
                print(f"Warning: <head> tag missing in {filename}, skipping injection.")

if __name__ == '__main__':
    inject_theme_script()
