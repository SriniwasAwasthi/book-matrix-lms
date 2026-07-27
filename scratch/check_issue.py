import sqlite3, os, json

db = r"e:\W c One Drive\MY THINKING\DBMS\library-system-BACKUP-2026-05-11_22-39\database\library.db"
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Tables
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]
print("Tables:", tables)

# Users
print("\n--- USERS ---")
c.execute("SELECT * FROM users")
for r in c.fetchall(): print(dict(r))

# Theme settings
print("\n--- THEME_SETTINGS ---")
c.execute("SELECT * FROM theme_settings")
for r in c.fetchall(): print(dict(r))

# User profiles
print("\n--- USER_PROFILES ---")
c.execute("SELECT * FROM user_profiles")
for r in c.fetchall(): print(dict(r))

# Library settings
print("\n--- LIBRARY_SETTINGS ---")
c.execute("SELECT * FROM library_settings")
for r in c.fetchall(): print(dict(r))

# Notifications count
c.execute("SELECT COUNT(*) FROM system_notifications")
print("\nSystem Notifications count:", c.fetchone()[0])

# Books count
c.execute("SELECT COUNT(*) FROM books")
print("Books count:", c.fetchone()[0])

conn.close()
