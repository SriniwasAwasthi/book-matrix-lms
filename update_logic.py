import os
import re

BASE_DIR = r"e:\W c One Drive\MY THINKING\DBMS\library-system-BACKUP-2026-05-11_22-39"
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
BACKEND_DIR = os.path.join(BASE_DIR, "backend")

# 1. Update style.css
style_path = os.path.join(FRONTEND_DIR, "style.css")
with open(style_path, 'r', encoding='utf-8') as f:
    style_content = f.read()

# Add Light Mode Variables if not fully present or correctly implemented
if 'body.light-mode' not in style_content:
    light_mode_css = """
body.light-mode {
    --deep-navy: #F8FAFC;
    --sidebar-bg: #FFFFFF;
    --card-bg: #FFFFFF;
    --glass-bg: #FFFFFF;
    --glass-border: #E2E8F0;
    --neon-blue: #2563EB;
    --neon-purple: #3B82F6;
    --text-primary: #0F172A;
    --text-secondary: #64748B;
    --shadow-glow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}
"""
    style_content = style_content.replace(':root {', light_mode_css + '\n:root {')

with open(style_path, 'w', encoding='utf-8') as f:
    f.write(style_content)

# 2. Update app.js
app_js_path = os.path.join(FRONTEND_DIR, "app.js")
with open(app_js_path, 'r', encoding='utf-8') as f:
    app_js_content = f.read()

# Add theme persistence
theme_script = """
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light-mode');
    }
});

function toggleTheme() {
    document.body.classList.toggle('light-mode');
    const isLight = document.body.classList.contains('light-mode');
    localStorage.setItem('theme', isLight ? 'light' : 'dark');
}
"""
if 'localStorage.getItem(\'theme\')' not in app_js_content:
    app_js_content += "\n" + theme_script

with open(app_js_path, 'w', encoding='utf-8') as f:
    f.write(app_js_content)

# 3. Update AI in server.py
server_path = os.path.join(BACKEND_DIR, "server.py")
with open(server_path, 'r', encoding='utf-8') as f:
    server_content = f.read()

# Just a simple hack: Replace the process_chat function definition and its body using regex or string splitting
parts = server_content.split('def process_chat(self, msg, c):')

new_process_chat = """def process_chat(self, msg, c):
        import re
        import random
        msg_lower = msg.lower().strip()
        
        greeting_replies = [
            "Welcome to BOOK MATRIX AI 📚\\nI can help you:\\n• Search books instantly\\n• Check availability\\n• Find authors and publishers\\n• View library statistics\\n• Track issued books\\n• Recommend books by category\\n• Answer library-related questions\\nStart by typing a book title, author name, category, or question."
        ]
        
        default_chips = ["Popular Categories", "Recently Added", "Most Borrowed", "Science", "Technology", "Business", "Fiction", "Self Help"]
        
        if any(g in msg_lower for g in ["hi", "hello", "hey", "greetings"]):
            return {"reply": greeting_replies[0], "books": [], "chips": default_chips}
            
        c.execute("SELECT * FROM books")
        all_books = c.fetchall()
        
        def get_serialized_books(rows):
            return [{"id": r["id"], "title": r["title"], "author": r["author"], "category": r["category"], "publisher": r["publisher"], "price": r["price"], "description": r["description"], "avail_qty": r["available_quantity"], "total_qty": r["total_quantity"], "rating": r["rating"] if "rating" in r.keys() else 4.5} for r in rows]
        
        # Level 4: Library Intelligence
        if "how many books" in msg_lower or "total books" in msg_lower or "available books" in msg_lower or "issued books" in msg_lower:
            c.execute("SELECT SUM(total_quantity), SUM(available_quantity) FROM books")
            t_qty, a_qty = c.fetchone()
            i_qty = t_qty - a_qty if t_qty and a_qty else 0
            return {"reply": f"There are {t_qty} copies in the library.\\n{a_qty} are currently available.\\n{i_qty} are issued.", "books": [], "chips": default_chips}
            
        # Level 1: Exact Book Search
        for b in all_books:
            if msg_lower == b['title'].lower() or msg_lower == b['author'].lower():
                return {"reply": f"Book Found\\nTitle: {b['title']}\\nAuthor: {b['author']}\\nCategory: {b['category']}\\nAvailability: {'Available' if b['available_quantity'] > 0 else 'Not Available'}", "books": get_serialized_books([b]), "chips": default_chips}
                
        # Level 2: Fuzzy Search
        for b in all_books:
            if msg_lower in b['title'].lower() or msg_lower in b['author'].lower() or b['title'].lower() in msg_lower:
                return {"reply": f"No exact match found. You may be interested in {b['title']}:", "books": get_serialized_books([b]), "chips": default_chips}
                
        # Level 3: Recommendation Engine
        c.execute("SELECT * FROM books ORDER BY rating DESC LIMIT 3")
        top_books = c.fetchall()
        top_titles = [b['title'] for b in top_books]
        return {"reply": f"We couldn't find that title.\\nPopular Books:\\n" + "\\n".join(f"• {t}" for t in top_titles), "books": get_serialized_books(top_books), "chips": default_chips}

if __name__ == '__main__':"""

if 'def process_chat(self, msg, c):' in server_content:
    new_server = parts[0] + new_process_chat + parts[1].split("if __name__ == '__main__':")[1]
    with open(server_path, 'w', encoding='utf-8') as f:
        f.write(new_server)

print("Update completed.")
