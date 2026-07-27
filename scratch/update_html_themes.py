import os

frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')

old_script_start = "    <!-- Task 6: Anti-Flicker theme loading script -->"

new_script_block = """    <!-- Task 6: Anti-Flicker theme loading script -->
    <script>
        (function() {
            if (window.location.protocol === 'file:') {
                const page = window.location.pathname.split('/').pop() || 'index.html';
                window.location.href = 'http://localhost:8085/' + page;
                return;
            }
            const theme = localStorage.getItem('theme') || 'dark';
            if (theme === 'light') {
                document.documentElement.classList.add('light-mode');
            } else {
                document.documentElement.classList.remove('light-mode');
            }
        })();
    </script>"""

count = 0
for filename in os.listdir(frontend_dir):
    if filename.endswith('.html'):
        file_path = os.path.join(frontend_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_script_start in content:
            # Locate the script block and replace it
            # The script block starts at old_script_start and ends at </script>
            start_idx = content.find(old_script_start)
            end_idx = content.find("</script>", start_idx)
            if end_idx != -1:
                end_idx += len("</script>")
                old_block = content[start_idx:end_idx]
                new_content = content.replace(old_block, new_script_block)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated anti-flicker script in {filename}")
                count += 1
            else:
                print(f"Warning: Could not find closing </script> in {filename}")
        else:
            print(f"No existing script in {filename}, injecting fresh one")
            if "<head>" in content:
                new_content = content.replace("<head>", "<head>\n" + new_script_block, 1)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Injected simplified script into {filename}")
                count += 1

print(f"Successfully processed {count} HTML files.")
