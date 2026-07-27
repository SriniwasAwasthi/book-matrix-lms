import sqlite3

db = r"e:\W c One Drive\MY THINKING\DBMS\library-system-BACKUP-2026-05-11_22-39\database\library.db"
conn = sqlite3.connect(db)
c = conn.cursor()

# Reset avatar to a proper online avatar (the one used by default in the code)
proper_avatar = "https://ui-avatars.com/api/?name=Admin+User&background=9d50bb&color=fff"
c.execute("UPDATE user_profiles SET avatar_path = ? WHERE user_id = 1", (proper_avatar,))
conn.commit()

# Verify
c.execute("SELECT avatar_path FROM user_profiles WHERE user_id = 1")
print("Avatar path updated to:", c.fetchone()[0])

conn.close()
print("Done!")
