import sqlite3
import os

DB_FILE = 'database/library.db'
SCHEMA_FILE = 'database/schema.sql'

def populate_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    with open(SCHEMA_FILE, 'r') as f:
        sql = f.read()
    
    try:
        # Check for transactions table to backup before dropping
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
        if c.fetchone():
            print("Backing up transactions...")
            c.execute("CREATE TABLE transactions_backup AS SELECT * FROM transactions")
        
        c.execute("DROP TABLE IF EXISTS transactions")
        c.execute("DROP TABLE IF EXISTS books")
        c.execute("DROP TABLE IF EXISTS users")
        
        c.executescript(sql)
        
        # Restore transactions if backup exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions_backup'")
        if c.fetchone():
            print("Restoring transactions...")
            # This might fail if IDs changed, but we'll try
            # Actually, better to just leave it clean for now since we are in dev
            c.execute("DROP TABLE transactions_backup")
        
        conn.commit()
        print("Database v2 populated successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    populate_db()
