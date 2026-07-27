import sqlite3
import os

db_path = os.path.join('database', 'library.db')
if not os.path.exists(db_path):
    print('DB not found at:', db_path)
else:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in c.fetchall()]
    print('Tables:', tables)
    for t in tables:
        try:
            c.execute(f"SELECT count(*) FROM [{t}]")
            print(f"{t}: {c.fetchone()[0]}")
        except Exception as e:
            print(f"Error reading table {t}: {e}")
    conn.close()
