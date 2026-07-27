import sqlite3
import os

DB_FILE = 'database/library.db'

def migrate_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    try:
        # Check if columns exist
        c.execute("PRAGMA table_info(books)")
        columns = [col[1] for col in c.fetchall()]
        
        if 'category' not in columns:
            print("Adding category column...")
            c.execute("ALTER TABLE books ADD COLUMN category TEXT DEFAULT 'Uncategorized'")
        
        if 'publisher' not in columns:
            print("Adding publisher column...")
            c.execute("ALTER TABLE books ADD COLUMN publisher TEXT DEFAULT 'Unknown'")
        
        conn.commit()
        print("Migration successful.")
    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_db()
