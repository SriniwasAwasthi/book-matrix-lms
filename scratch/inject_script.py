import os

frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')

script_block = """    <!-- Task 6: Anti-Flicker theme loading script -->
    <script>
        (function() {
            const theme = localStorage.getItem('theme') || 'dark';
            const sidebarStyle = localStorage.getItem('sidebar_style') || 'Glassmorphism (Default)';
            if (theme === 'light') {
                document.documentElement.classList.add('light-mode');
            } else {
                document.documentElement.classList.remove('light-mode');
            }
            document.documentElement.classList.remove('theme-solid-dark', 'theme-solid-light', 'theme-glassmorphism');
            if (sidebarStyle === 'Solid Dark') {
                document.documentElement.classList.add('theme-solid-dark');
            } else if (sidebarStyle === 'Solid Light') {
                document.documentElement.classList.add('theme-solid-light');
            } else {
                document.documentElement.classList.add('theme-glassmorphism');
            }
        })();
    </script>"""

count = 0
for filename in os.listdir(frontend_dir):
    if filename.endswith('.html'):
        file_path = os.path.join(frontend_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already injected
        if "Task 6: Anti-Flicker theme loading script" in content:
            print(f"Skipping {filename} - script already injected.")
            continue
            
        # We find <head> and insert right after it
        if "<head>" in content:
            new_content = content.replace("<head>", "<head>\n" + script_block, 1)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Injected anti-flicker script into {filename}")
            count += 1
        else:
            print(f"Warning: Could not find <head> in {filename}")

print(f"Successfully processed HTML files. Injected into {count} files.")
