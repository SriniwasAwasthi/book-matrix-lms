import sqlite3
import os

def run_migrations_v3():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'library.db'))
    print(f"Applying Settings Module Migrations (v3) to: {db_path}")

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        # Enable WAL mode for concurrency protection
        c.execute("PRAGMA journal_mode=WAL;")
        print("Enabled WAL (Write-Ahead Logging) mode.")

        # Enable foreign keys
        c.execute("PRAGMA foreign_keys=ON;")

        # 1. Create User Preferences Table
        c.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY,
                session_timeout INTEGER DEFAULT 30,
                max_login_attempts INTEGER DEFAULT 5,
                lock_duration INTEGER DEFAULT 15,
                auto_logout INTEGER DEFAULT 1,
                email_otp INTEGER DEFAULT 0,
                authenticator_app INTEGER DEFAULT 0,
                backup_schedule TEXT CHECK(backup_schedule IN ('none', 'daily', 'weekly', 'monthly')) DEFAULT 'none',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        print("Table 'user_preferences' verified/created.")

        # 2. Create Login History Table
        c.execute("""
            CREATE TABLE IF NOT EXISTS login_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                ip_address TEXT,
                device_info TEXT,
                status TEXT CHECK(status IN ('Success', 'Failed')) NOT NULL,
                failure_reason TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("Table 'login_history' verified/created.")

        # 3. Create System Notifications Table
        c.execute("""
            CREATE TABLE IF NOT EXISTS system_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT CHECK(type IN ('Dashboard', 'Maintenance', 'Database', 'Security')) DEFAULT 'Dashboard',
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        print("Table 'system_notifications' verified/created.")

        # 4. Check & Add Typography Columns to theme_settings
        c.execute("PRAGMA table_info(theme_settings);")
        columns = [row[1] for row in c.fetchall()]

        typography_cols = {
            'font_size': "TEXT DEFAULT '14px'",
            'font_weight': "TEXT DEFAULT 'normal'",
            'letter_spacing': "TEXT DEFAULT '0px'",
            'line_height': "TEXT DEFAULT '1.6'"
        }

        for col, col_def in typography_cols.items():
            if col not in columns:
                c.execute(f"ALTER TABLE theme_settings ADD COLUMN {col} {col_def};")
                print(f"Added column '{col}' to table 'theme_settings'.")
            else:
                print(f"Column '{col}' already exists in table 'theme_settings'.")

        # 5. Insert sample notifications to populate UI
        c.execute("SELECT id FROM users ORDER BY id LIMIT 1")
        user_row = c.fetchone()
        user_id = user_row[0] if user_row else 1

        c.execute("SELECT COUNT(*) FROM system_notifications")
        if c.fetchone()[0] == 0:
            c.execute("""
                INSERT INTO system_notifications (user_id, type, title, message, is_read) VALUES
                (?, 'Dashboard', 'System Initialized', 'Book Matrix Settings module successfully integrated with database backup services.', 0),
                (?, 'Security', 'Admin Session Verified', 'Active login token validated successfully from standard IP address.', 0),
                (?, 'Database', 'Scheduled Backup Executed', 'Automated compression backup completed in 12ms under status: Success.', 1)
            """, (user_id, user_id, user_id))
            print("Seeded sample alerts into 'system_notifications'.")

        conn.commit()
        print("Database migrations applied successfully!")

    except Exception as e:
        conn.rollback()
        print(f"Migration error occurred: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    run_migrations_v3()
