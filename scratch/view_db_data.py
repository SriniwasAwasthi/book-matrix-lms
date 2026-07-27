import sqlite3
import os

db_path = os.path.join('database', 'library.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    print("--- USERS ---")
    c.execute("SELECT * FROM users LIMIT 10")
    for row in c.fetchall():
        print(row)
        
    print("\n--- BOOKS (first 5) ---")
    c.execute("SELECT id, title, author, category, available_quantity, total_quantity FROM books LIMIT 5")
    for row in c.fetchall():
        print(row)
        
    conn.close()
else:
    print("No database found.")
