import sqlite3
import os

def run_migrations():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'library.db'))
    schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql'))
    
    print(f"Applying schema from: {schema_path}")
    print(f"Target Database: {db_path}")
    
    if not os.path.exists(schema_path):
        print("Error: schema.sql not found!")
        return
        
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
        
    # Split to run only the extensions to prevent UNIQUE constraint re-insert errors
    if "-- Extended Tables for Book Matrix Settings" in schema_sql:
        extensions_sql = schema_sql.split("-- Extended Tables for Book Matrix Settings")[1]
    else:
        extensions_sql = schema_sql
        
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(extensions_sql)
        conn.commit()
        print("Database migration executed successfully!")
        
        # Verify the tables created
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in c.fetchall()]
        print(f"Active database tables: {tables}")
    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    run_migrations()
