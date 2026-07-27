import sqlite3
import os

DB_FILE = r'c:\Users\sriaw\OneDrive\Desktop\MY THINKING\WANNA - Copy\library-system\database\library.db'

def check():
    if not os.path.exists(DB_FILE):
        print("Database file not found.")
        return
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    print("Tables:")
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    for table in tables:
        print(f"\nTable: {table[0]}")
        c.execute(f"PRAGMA table_info({table[0]})")
        columns = c.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
            
    c.execute("SELECT COUNT(*) FROM books")
    print(f"\nBook count: {c.fetchone()[0]}")
    
    conn.close()

if __name__ == "__main__":
    check()
