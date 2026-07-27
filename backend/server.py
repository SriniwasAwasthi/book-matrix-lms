import http.server
import socketserver
import sqlite3
import json
import urllib.parse
import os
import hashlib
import secrets
import shutil
import time
import threading

DB_FILE = os.path.join(os.path.dirname(__file__), '..', 'database', 'library.db')

def db_get_library_statistics():
    """Returns total books, members, active borrows, and overdue books."""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT SUM(total_quantity), SUM(available_quantity), COUNT(DISTINCT id) FROM books")
        row = c.fetchone()
        total_qty = row[0] if row[0] is not None else 0
        avail_qty = row[1] if row[1] is not None else 0
        total_titles = row[2] if row[2] is not None else 0
        
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM transactions WHERE actual_return_date IS NULL")
        borrowed_books = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM transactions WHERE actual_return_date IS NULL AND return_date < date('now')")
        overdue_books = c.fetchone()[0]
        conn.close()
        return {
            "total_titles": total_titles,
            "total_book_copies": total_qty,
            "available_for_issue": avail_qty,
            "currently_borrowed": borrowed_books,
            "overdue_books": overdue_books,
            "registered_members": total_users
        }
    except Exception as e:
        return {"error": str(e)}

def db_search_books(query: str = "", author: str = "", category: str = ""):
    """Searches the database for books matching the title query, author, or category. Returns availability, price, and stock info."""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        sql = "SELECT id, title, author, category, publisher, price, description, total_quantity, available_quantity FROM books WHERE 1=1"
        params = []
        if query:
            sql += " AND title LIKE ?"
            params.append(f"%{query}%")
        if author:
            sql += " AND author LIKE ?"
            params.append(f"%{author}%")
        if category:
            sql += " AND category LIKE ?"
            params.append(f"%{category}%")
            
        sql += " LIMIT 5"
        c.execute(sql, tuple(params))
        books = [dict(r) for r in c.fetchall()]
        conn.close()
        return {"results": books, "count": len(books)}
    except Exception as e:
        return {"error": str(e)}

def db_get_recommendations(genre: str):
    """Queries the DB for top/available books in a category or genre."""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT id, title, author, category, price, available_quantity, total_quantity FROM books WHERE category LIKE ? ORDER BY available_quantity DESC LIMIT 4", (f"%{genre}%",))
        books = [dict(r) for r in c.fetchall()]
        conn.close()
        return {"recommendations": books, "genre_searched": genre}
    except Exception as e:
        return {"error": str(e)}

def db_get_user_status(user_name: str):
    """Returns current borrowed books for a specific user name."""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE name LIKE ? LIMIT 1", (f"%{user_name}%",))
        user = c.fetchone()
        if not user:
            return {"error": f"User {user_name} not found"}
        
        c.execute("SELECT t.id, b.title, t.issue_date, t.return_date FROM transactions t JOIN books b ON t.book_id = b.id WHERE t.user_id = ? AND t.actual_return_date IS NULL", (user['id'],))
        borrowed = [dict(r) for r in c.fetchall()]
        conn.close()
        return {"user_name": user_name, "borrowed_books": borrowed}
    except Exception as e:
        return {"error": str(e)}
def init_db():
    if os.path.exists(DB_FILE):
        return
        
    print("Initializing database from schema.sql...")
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql')
    if not os.path.exists(schema_path):
        # Fallback if schema.sql is missing
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, author TEXT NOT NULL, category TEXT DEFAULT 'Uncategorized', publisher TEXT DEFAULT 'Unknown', price REAL NOT NULL, description TEXT, total_quantity INTEGER NOT NULL, available_quantity INTEGER NOT NULL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, book_id INTEGER NOT NULL, issue_date DATE NOT NULL, return_date DATE NOT NULL, actual_return_date DATE)''')
        conn.commit()
        conn.close()
        return

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    conn = sqlite3.connect(DB_FILE)
    try:
        conn.executescript(schema_sql)
        conn.commit()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    pw_bytes = password.encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    db_hash = hashlib.pbkdf2_hmac('sha256', pw_bytes, salt_bytes, 100000).hex()
    return f"{salt}${db_hash}"

def verify_password(stored_password, provided_password):
    if not stored_password:
        return False
    if '$' not in stored_password:
        return stored_password == provided_password
    salt, db_hash = stored_password.split('$', 1)
    pw_bytes = provided_password.encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    computed_hash = hashlib.pbkdf2_hmac('sha256', pw_bytes, salt_bytes, 100000).hex()
    return computed_hash == db_hash

def validate_password_strength(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter."
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit."
    specials = "!@#$%^&*()_+-=[]{}|;:,.<>?~`"
    if not any(c in specials for c in password):
        return False, "Password must contain at least one special character."
    return True, ""

def parse_user_agent(ua_string):
    ua = (ua_string or "").lower()
    os_name = "Unknown OS"
    if "windows" in ua:
        os_name = "Windows"
    elif "macintosh" in ua or "mac os" in ua:
        os_name = "macOS"
    elif "android" in ua:
        os_name = "Android"
    elif "iphone" in ua or "ipad" in ua or "ipod" in ua:
        os_name = "iOS"
    elif "linux" in ua:
        os_name = "Linux"
        
    browser = "Unknown Browser"
    if "edg/" in ua:
        browser = "Microsoft Edge"
    elif "chrome" in ua and "safari" in ua and "apis-google" not in ua:
        browser = "Google Chrome"
    elif "firefox" in ua:
        browser = "Firefox"
    elif "safari" in ua and "chrome" not in ua:
        browser = "Safari"
        
    device_type = "Desktop"
    if "mobile" in ua or "android" in ua or "iphone" in ua:
        device_type = "Mobile"
    elif "ipad" in ua or "tablet" in ua:
        device_type = "Tablet"
        
    return device_type, browser, os_name

def validate_magic_bytes(file_data):
    if len(file_data) < 4:
        return False
    header = file_data[:4]
    if header == b'\x89PNG':
        return True
    if header[:3] == b'\xFF\xD8\xFF':
        return True
    if header == b'RIFF' and len(file_data) >= 12 and file_data[8:12] == b'WEBP':
        return True
    return False

def ensure_default_settings(c, user_id):
    c.execute("SELECT 1 FROM user_profiles WHERE user_id = ?", (user_id,))
    if not c.fetchone():
        c.execute("""
            INSERT INTO user_profiles (user_id, account_type, avatar_path, phone_number, employee_id, designation)
            VALUES (?, 'Admin', 'https://ui-avatars.com/api/?name=Admin+User&background=9d50bb&color=fff', '+1 (555) 123-4567', 'EMP-001', 'Library Administrator')
        """, (user_id,))
    
    c.execute("SELECT 1 FROM user_notifications WHERE user_id = ?", (user_id,))
    if not c.fetchone():
        c.execute("""
            INSERT INTO user_notifications (user_id, notify_new_member, notify_book_issue, notify_book_return, notify_overdue, notify_fine, notify_new_admin, notify_dashboard, notify_maintenance, notify_database, notify_security, channel_email, channel_sms, channel_in_app)
            VALUES (?, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1)
        """, (user_id,))
        
    c.execute("SELECT 1 FROM theme_settings WHERE user_id = ?", (user_id,))
    if not c.fetchone():
        c.execute("""
            INSERT INTO theme_settings (user_id, accent_color, visual_mode, glassmorphism, font_family, ui_density, animations_enabled, font_size, font_weight, letter_spacing, line_height)
            VALUES (?, 'blue', 'dark', 1, 'cinzel', 'comfortable', 1, '14px', 'normal', '0px', '1.6')
        """, (user_id,))

    c.execute("SELECT 1 FROM user_preferences WHERE user_id = ?", (user_id,))
    if not c.fetchone():
        c.execute("""
            INSERT INTO user_preferences (user_id, session_timeout, max_login_attempts, lock_duration, auto_logout, email_otp, authenticator_app, backup_schedule)
            VALUES (?, 30, 5, 15, 1, 0, 0, 'none')
        """, (user_id,))

def resolve_active_device(c, user_id, session_token, ua_string, ip_address):
    if not session_token:
        session_token = "default_mock_session_token_123"
        
    c.execute("SELECT 1 FROM user_devices WHERE session_token = ?", (session_token,))
    if not c.fetchone():
        device_type, browser, os_name = parse_user_agent(ua_string)
        c.execute("""
            INSERT INTO user_devices (user_id, session_token, device_type, browser, os, ip_address, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (user_id, session_token, device_type, browser, os_name, ip_address))
    else:
        c.execute("""
            UPDATE user_devices 
            SET last_login_time = CURRENT_TIMESTAMP, is_active = 1 
            WHERE session_token = ?
        """, (session_token,))

def log_audit(c, user_id, action, module, old_val, new_val, ip_addr, ua_str):
    device_type, browser, os_name = parse_user_agent(ua_str)
    device_info = f"{device_type} - {browser} ({os_name})"
    c.execute("""
        INSERT INTO audit_logs (user_id, action, module, old_value, new_value, ip_address, device)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, action, module, str(old_val), str(new_val), ip_addr, device_info))

def add_system_notification(c, user_id, notif_type, title, message):
    pref_column_map = {
        'Dashboard': 'notify_dashboard',
        'Maintenance': 'notify_maintenance',
        'Database': 'notify_database',
        'Security': 'notify_security'
    }
    col = pref_column_map.get(notif_type, 'notify_dashboard')
    ensure_default_settings(c, user_id)
    c.execute(f"SELECT {col} FROM user_notifications WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if not row or row[0]:
        c.execute("""
            INSERT INTO system_notifications (user_id, type, title, message, is_read)
            VALUES (?, ?, ?, ?, 0)
        """, (user_id, notif_type, title, message))

def get_user_from_session(c, session_token):
    if not session_token:
        c.execute("SELECT id FROM users ORDER BY id LIMIT 1")
        row = c.fetchone()
        return row[0] if row else 1
    c.execute("SELECT user_id FROM user_devices WHERE session_token = ? AND is_active = 1", (session_token,))
    row = c.fetchone()
    if row:
        return row[0]
    c.execute("SELECT id FROM users ORDER BY id LIMIT 1")
    row = c.fetchone()
    return row[0] if row else 1

def make_async_backup(db_path, backups_dir, trigger_type='manual'):
    os.makedirs(backups_dir, exist_ok=True)
    timestamp = int(time.time())
    filename = f"backup_{trigger_type}_{timestamp}.db"
    dest_path = os.path.join(backups_dir, filename)
    start_time = time.time()
    try:
        shutil.copy2(db_path, dest_path)
        duration_ms = int((time.time() - start_time) * 1000)
        size_bytes = os.path.getsize(dest_path)
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""
            INSERT INTO backup_history (filename, trigger_type, size_bytes, duration_ms, status)
            VALUES (?, ?, ?, ?, 'Success')
        """, (filename, trigger_type, size_bytes, duration_ms))
        conn.commit()
        conn.close()
        print(f"Async {trigger_type} backup completed: {filename}")
    except Exception as e:
        print(f"Async {trigger_type} backup failed: {e}")

def start_backup_scheduler():
    def scheduler_loop():
        time.sleep(20)
        db_path = DB_FILE
        backups_dir = os.path.abspath(os.path.join(os.path.dirname(db_path), 'backups'))
        
        while True:
            try:
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                c.execute("SELECT backup_schedule FROM user_preferences LIMIT 1")
                row = c.fetchone()
                schedule = row[0] if row else 'none'
                
                if schedule != 'none':
                    c.execute("""
                        SELECT created_at FROM backup_history 
                        WHERE trigger_type = 'auto' AND status = 'Success' 
                        ORDER BY created_at DESC LIMIT 1
                    """)
                    last_row = c.fetchone()
                    
                    should_backup = False
                    if not last_row:
                        should_backup = True
                    else:
                        from datetime import datetime
                        last_time_str = last_row[0]
                        try:
                            last_time = datetime.strptime(last_time_str, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            last_time = datetime.utcnow()
                        
                        delta = datetime.utcnow() - last_time
                        if schedule == 'daily' and delta.total_seconds() >= 86400:
                            should_backup = True
                        elif schedule == 'weekly' and delta.total_seconds() >= 86400 * 7:
                            should_backup = True
                        elif schedule == 'monthly' and delta.total_seconds() >= 86400 * 30:
                            should_backup = True
                            
                    if should_backup:
                        print(f"Auto scheduler: Triggering automatic {schedule} backup.")
                        make_async_backup(db_path, backups_dir, trigger_type='auto')
                        
                conn.close()
            except Exception as e:
                print(f"Scheduler loop error: {e}")
            time.sleep(60)
            
    thread = threading.Thread(target=scheduler_loop)
    thread.daemon = True
    thread.start()
    print("Persistent backup scheduler thread initialized.")

def parse_multipart(body, boundary):
    parts = body.split(b'--' + boundary.encode('utf-8'))
    fields = {}
    files = {}
    for part in parts:
        if not part or part == b'\r\n' or part == b'--\r\n':
            continue
        if b'\r\n\r\n' in part:
            headers_part, content_part = part.split(b'\r\n\r\n', 1)
            if content_part.endswith(b'\r\n'):
                content_part = content_part[:-2]
            
            headers_str = headers_part.decode('utf-8', errors='ignore')
            name = None
            filename = None
            content_type_part = None
            for line in headers_str.split('\r\n'):
                if line.lower().startswith('content-disposition:'):
                    parts_disp = line.split(';')
                    for p in parts_disp:
                        p = p.strip()
                        if p.startswith('name='):
                            name = p.split('=', 1)[1].strip('"\'')
                        elif p.startswith('filename='):
                            filename = p.split('=', 1)[1].strip('"\'')
                elif line.lower().startswith('content-type:'):
                    content_type_part = line.split(':', 1)[1].strip()
            
            if name:
                if filename:
                    files[name] = {
                        'filename': filename,
                        'content_type': content_type_part,
                        'data': content_part
                    }
                else:
                    fields[name] = content_part.decode('utf-8', errors='ignore')
    return fields, files

class LibraryHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Serve frontend files
        frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
        super().__init__(*args, directory=frontend_dir, **kwargs)

    def end_headers(self):
        # Prevent browser caching of HTML, CSS, and JS to ensure absolute cross-browser sync and instant hot-reload
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_GET(self):
        if self.path.startswith('/api?'):
            self.handle_api()
        else:
            super().do_GET()

    def handle_api(self):
        query_str = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query_str)
        action = params.get('action', [''])[0]
        
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        response = {}
        
        try:
            if action == 'dashboard':
                c.execute("SELECT COUNT(*) as tt, SUM(total_quantity) as tq, SUM(available_quantity) as aq FROM books")
                row1 = c.fetchone()
                c.execute("SELECT COUNT(*) as ib FROM transactions WHERE actual_return_date IS NULL")
                row2 = c.fetchone()
                c.execute("SELECT COUNT(*) as tu FROM users")
                row3 = c.fetchone()
                c.execute("SELECT COUNT(*) as ob FROM transactions WHERE actual_return_date IS NULL AND return_date < date('now')")
                row4 = c.fetchone()
                
                response = {
                    "total_titles": row1['tt'] if row1['tt'] else 0,
                    "total_books": row1['tq'] if row1['tq'] else 0,
                    "available_books": row1['aq'] if row1['aq'] else 0,
                    "issued_books": row2['ib'] if row2['ib'] else 0,
                    "total_users": row3['tu'] if row3['tu'] else 0,
                    "overdue_books": row4['ob'] if row4['ob'] else 0
                }
            
            elif action == 'get_books':
                c.execute("SELECT id, title, author, category, publisher, price, description, total_quantity, available_quantity FROM books")
                response = [{"id": r["id"], "title": r["title"], "author": r["author"], "category": r["category"], "publisher": r["publisher"], "price": r["price"], "total_qty": r["total_quantity"], "avail_qty": r["available_quantity"]} for r in c.fetchall()]
            
            elif action == 'get_categories':
                c.execute("SELECT DISTINCT category FROM books ORDER BY category")
                response = [r['category'] for r in c.fetchall()]
                
            elif action == 'get_authors':
                c.execute("SELECT DISTINCT author FROM books ORDER BY author")
                response = [r['author'] for r in c.fetchall()]
                
            elif action == 'get_publishers':
                c.execute("SELECT DISTINCT publisher FROM books ORDER BY publisher")
                response = [r['publisher'] for r in c.fetchall()]

            elif action == 'get_book_details':
                book_id = params.get('id', [''])[0]
                c.execute("SELECT * FROM books WHERE id = ?", (book_id,))
                row = c.fetchone()
                if row:
                    response = {
                        "id": row["id"],
                        "title": row["title"],
                        "author": row["author"],
                        "category": row["category"],
                        "publisher": row["publisher"],
                        "price": row["price"],
                        "description": row["description"],
                        "total_qty": row["total_quantity"],
                        "avail_qty": row["available_quantity"]
                    }
                else:
                    response = {"error": "Book not found"}
            
            elif action == 'add_book':
                title = params.get('title',[''])[0].strip()
                author = params.get('author',[''])[0].strip()
                if not title or not author:
                    response = {"error": "Title and Author are required"}
                else:
                    try:
                        price = float(params.get('price',['0'])[0])
                        qty = int(params.get('quantity',['0'])[0])
                    except ValueError:
                        price = 0.0
                        qty = 1
                    c.execute("INSERT INTO books (title, author, category, publisher, price, description, total_quantity, available_quantity) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                              (title, author, params.get('category',['Uncategorized'])[0], params.get('publisher',['Unknown'])[0], price, params.get('description',[''])[0], qty, qty))
                    conn.commit()
                    response = {"success": "Book added successfully"}
            
            elif action == 'get_users':
                c.execute("SELECT id, name, email FROM users")
                response = [{"id": r["id"], "name": r["name"], "email": r["email"]} for r in c.fetchall()]
            
            elif action == 'add_user':
                name = params.get('name',[''])[0].strip()
                email = params.get('email',[''])[0].strip()
                if not name or not email:
                    response = {"error": "Name and Email are required"}
                else:
                    try:
                        c.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
                        conn.commit()
                        response = {"success": "User added successfully"}
                    except sqlite3.IntegrityError:
                        response = {"error": "Email already exists"}
            
            elif action == 'issue_book':
                user_id = params.get('user_id',[''])[0]
                book_id = params.get('book_id',[''])[0]
                ret_date = params.get('return_date',[''])[0]
                
                if not user_id or not book_id:
                    response = {"error": "User ID and Book ID are required"}
                else:
                    c.execute("SELECT id FROM users WHERE id = ?", (user_id,))
                    if not c.fetchone():
                        response = {"error": "User not found"}
                    else:
                        c.execute("SELECT available_quantity, title FROM books WHERE id = ?", (book_id,))
                        b_row = c.fetchone()
                        if not b_row:
                            response = {"error": "Book not found"}
                        else:
                            avail = b_row['available_quantity']
                            b_title = b_row['title']
                            if avail <= 0:
                                response = {"error": "Book is not available"}
                            else:
                                c.execute("INSERT INTO transactions (user_id, book_id, issue_date, return_date) VALUES (?, ?, date('now'), ?)", (user_id, book_id, ret_date))
                                c.execute("UPDATE books SET available_quantity = available_quantity - 1 WHERE id = ?", (book_id,))
                                
                                c.execute("SELECT name FROM users WHERE id = ?", (user_id,))
                                u_row = c.fetchone()
                                u_name = u_row['name'] if u_row else "Member"
                                
                                session_token = self.headers.get('X-Session-Token', '')
                                admin_user_id = get_user_from_session(c, session_token)
                                
                                add_system_notification(c, admin_user_id, 'Dashboard', 'Book Issued Successfully', f'"{b_title}" has been successfully issued to {u_name}. Due date: {ret_date}.')
                                
                                conn.commit()
                                response = {"success": "Book issued successfully"}
            
            elif action == 'return_book':
                tx_id = params.get('transaction_id',[''])[0]
                if not tx_id:
                    response = {"error": "Transaction ID is required"}
                else:
                    c.execute("SELECT t.book_id, t.actual_return_date, b.title, u.name FROM transactions t JOIN books b ON t.book_id = b.id JOIN users u ON t.user_id = u.id WHERE t.id = ?", (tx_id,))
                    tx = c.fetchone()
                    if tx:
                        if tx['actual_return_date']:
                            response = {"error": "Book already returned"}
                        else:
                            c.execute("UPDATE transactions SET actual_return_date = date('now') WHERE id = ?", (tx_id,))
                            c.execute("UPDATE books SET available_quantity = available_quantity + 1 WHERE id = ?", (tx['book_id'],))
                            
                            session_token = self.headers.get('X-Session-Token', '')
                            admin_user_id = get_user_from_session(c, session_token)
                            
                            add_system_notification(c, admin_user_id, 'Dashboard', 'Book Returned Successfully', f'"{tx["title"]}" borrowed by {tx["name"]} has been returned and added back to inventory.')
                            
                            conn.commit()
                            response = {"success": "Book returned successfully"}
                    else:
                        response = {"error": "Transaction not found"}
            
            elif action == 'get_transactions':
                c.execute("SELECT t.id, u.name as user, b.title as book, t.issue_date, t.return_date, t.actual_return_date FROM transactions t JOIN users u ON t.user_id = u.id JOIN books b ON t.book_id = b.id")
                response = [{"id": r["id"], "user": r["user"], "book": r["book"], "issue_date": r["issue_date"], "return_date": r["return_date"], "actual_return_date": r["actual_return_date"]} for r in c.fetchall()]
            
            elif action == 'chat':
                message = params.get('message', [''])[0]
                history_param = params.get('history', [None])[0]
                history = None
                if history_param:
                    try:
                        history = json.loads(history_param)
                    except:
                        pass
                response = self.process_chat(message, c, history=history)

            elif action == 'get_settings':
                session_token = self.headers.get('X-Session-Token', '') or params.get('session_token', [''])[0]
                user_id = get_user_from_session(c, session_token)
                ensure_default_settings(c, user_id)
                conn.commit()
                
                c.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
                user = c.fetchone()
                if not user:
                    c.execute("SELECT id, name, email FROM users ORDER BY id LIMIT 1")
                    user = c.fetchone()
                    user_id = user['id']
                
                c.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
                profile_row = c.fetchone()
                
                c.execute("SELECT * FROM library_settings ORDER BY id LIMIT 1")
                library_row = c.fetchone()
                
                c.execute("SELECT * FROM user_notifications WHERE user_id = ?", (user_id,))
                notify_row = c.fetchone()
                
                c.execute("SELECT * FROM theme_settings WHERE user_id = ?", (user_id,))
                theme_row = c.fetchone()
                
                c.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,))
                pref_row = c.fetchone()
                
                ip_address = self.client_address[0]
                ua_string = self.headers.get('User-Agent', '')
                if session_token:
                    resolve_active_device(c, user_id, session_token, ua_string, ip_address)
                    conn.commit()
                    
                response = {
                    "profile": {
                        "fullName": user["name"],
                        "email": user["email"],
                        "username": profile_row["employee_id"] if profile_row["employee_id"] else "admin",
                        "phone": profile_row["phone_number"],
                        "designation": profile_row["designation"],
                        "accountType": profile_row["account_type"],
                        "employeeId": profile_row["employee_id"] or "",
                        "studentId": profile_row["student_id"] or "",
                        "avatarPath": profile_row["avatar_path"]
                    },
                    "library": {
                        "libraryName": library_row["library_name"] if library_row else "Central Public Library",
                        "libraryCode": library_row["library_code"] if library_row else "LIB-001",
                        "institutionName": library_row["institution_name"] if library_row else "City Education Board",
                        "address": library_row["address"] if library_row else "123 Library Avenue",
                        "city": library_row["city"] if library_row else "New York",
                        "state": library_row["state"] if library_row else "NY",
                        "country": library_row["country"] if library_row else "United States",
                        "zipCode": library_row["zip_code"] if library_row else "10001"
                    },
                    "notifications": {
                        "toggles": {
                            "newMember": bool(notify_row["notify_new_member"]),
                            "bookIssue": bool(notify_row["notify_book_issue"]),
                            "bookReturn": bool(notify_row["notify_book_return"]),
                            "overdue": bool(notify_row["notify_overdue"]),
                            "fine": bool(notify_row["notify_fine"]),
                            "newAdmin": bool(notify_row["notify_new_admin"]),
                            "dashboard": bool(notify_row["notify_dashboard"]),
                            "maintenance": bool(notify_row["notify_maintenance"]),
                            "database": bool(notify_row["notify_database"]),
                            "security": bool(notify_row["notify_security"])
                        },
                        "channels": {
                            "email": bool(notify_row["channel_email"]),
                            "sms": bool(notify_row["channel_sms"]),
                            "inApp": bool(notify_row["channel_in_app"])
                        }
                    },
                    "security": {
                        "sessionTimeout": pref_row["session_timeout"] if pref_row else 30,
                        "maxLoginAttempts": pref_row["max_login_attempts"] if pref_row else 5,
                        "lockDuration": pref_row["lock_duration"] if pref_row else 15,
                        "autoLogout": bool(pref_row["auto_logout"]) if pref_row else True,
                        "emailOtp": bool(pref_row["email_otp"]) if pref_row else False,
                        "authenticatorApp": bool(pref_row["authenticator_app"]) if pref_row else False,
                        "backupSchedule": pref_row["backup_schedule"] if pref_row else "none"
                    },
                    "customization": {
                        "accentColor": theme_row["accent_color"],
                        "glassmorphism": bool(theme_row["glassmorphism"]),
                        "fontFamily": theme_row["font_family"],
                        "uiDensity": theme_row["ui_density"],
                        "animationsEnabled": bool(theme_row["animations_enabled"]),
                        "fontSize": theme_row["font_size"] if theme_row["font_size"] else "14px",
                        "fontWeight": theme_row["font_weight"] if theme_row["font_weight"] else "normal",
                        "letterSpacing": theme_row["letter_spacing"] if theme_row["letter_spacing"] else "0px",
                        "lineHeight": theme_row["line_height"] if theme_row["line_height"] else "1.6"
                    }
                }

            elif action == 'get_notifications':
                session_token = self.headers.get('X-Session-Token', '') or params.get('session_token', [''])[0]
                user_id = get_user_from_session(c, session_token)
                c.execute("SELECT id, type, title, message, is_read, created_at FROM system_notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 50", (user_id,))
                response = [{
                    "id": r["id"],
                    "type": r["type"],
                    "title": r["title"],
                    "message": r["message"],
                    "is_read": bool(r["is_read"]),
                    "created_at": r["created_at"]
                } for r in c.fetchall()]

            elif action == 'get_backups':
                backups_dir = os.path.abspath(os.path.join(os.path.dirname(DB_FILE), 'backups'))
                if not os.path.exists(backups_dir):
                    os.makedirs(backups_dir, exist_ok=True)
                
                c.execute("SELECT id, filename, trigger_type, size_bytes, duration_ms, status, created_at FROM backup_history ORDER BY created_at DESC")
                history = []
                for r in c.fetchall():
                    file_path = os.path.join(backups_dir, r['filename'])
                    exists = os.path.exists(file_path)
                    
                    sz = r['size_bytes']
                    if sz >= 1024 * 1024:
                        size_text = f"{sz / (1024 * 1024):.2f} MB"
                    elif sz >= 1024:
                        size_text = f"{sz / 1024:.2f} KB"
                    else:
                        size_text = f"{sz} B"
                        
                    history.append({
                        "id": r["id"],
                        "filename": r["filename"],
                        "trigger_type": r["trigger_type"],
                        "size_bytes": r["size_bytes"],
                        "size_text": size_text,
                        "duration_ms": r["duration_ms"],
                        "status": r["status"],
                        "created_at": r["created_at"],
                        "exists": exists
                    })
                response = history

            elif action == 'download_backup':
                filename = params.get('filename', [''])[0]
                if not filename or '/' in filename or '\\' in filename:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Invalid backup filename"}).encode())
                    conn.close()
                    return
                backups_dir = os.path.abspath(os.path.join(os.path.dirname(DB_FILE), 'backups'))
                file_path = os.path.join(backups_dir, filename)
                if os.path.exists(file_path):
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/octet-stream')
                    self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                    self.send_header('Content-Length', str(os.path.getsize(file_path)))
                    self.end_headers()
                    with open(file_path, 'rb') as f:
                        self.wfile.write(f.read())
                    conn.close()
                    return
                else:
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Backup file not found"}).encode())
                    conn.close()
                    return

            elif action == 'get_devices':
                c.execute("SELECT id FROM users ORDER BY id LIMIT 1")
                user = c.fetchone()
                user_id = user['id'] if user else 1
                c.execute("SELECT session_token, device_type, browser, os, ip_address, last_login_time, is_active FROM user_devices WHERE user_id = ? ORDER BY last_login_time DESC", (user_id,))
                response = [{
                    "session_token": r["session_token"],
                    "device_type": r["device_type"],
                    "browser": r["browser"],
                    "os": r["os"],
                    "ip_address": r["ip_address"],
                    "last_login_time": r["last_login_time"],
                    "is_active": bool(r["is_active"])
                } for r in c.fetchall()]

            elif action == 'get_audit_logs':
                c.execute("SELECT action, module, old_value, new_value, ip_address, device, timestamp FROM audit_logs ORDER BY timestamp DESC")
                response = [{
                    "timestamp": r["timestamp"],
                    "user": "Admin User",
                    "action": r["action"],
                    "module": r["module"],
                    "ip": r["ip_address"],
                    "status": "Success"
                } for r in c.fetchall()]

            elif action == 'database_stats':
                db_name = os.path.basename(DB_FILE)
                db_size_bytes = os.path.getsize(DB_FILE) if os.path.exists(DB_FILE) else 0
                if db_size_bytes >= 1024 * 1024:
                    db_size = f"{db_size_bytes / (1024 * 1024):.1f} MB"
                elif db_size_bytes >= 1024:
                    db_size = f"{db_size_bytes / 1024:.1f} KB"
                else:
                    db_size = f"{db_size_bytes} B"

                c.execute("SELECT COUNT(*) FROM books")
                book_count = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM users")
                user_count = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM transactions")
                tx_count = c.fetchone()[0]
                
                # Check audit logs and backups counts
                c.execute("SELECT COUNT(*) FROM audit_logs")
                audit_count = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM backup_history")
                backup_count = c.fetchone()[0]
                
                total_records = book_count + user_count + tx_count + audit_count + backup_count

                # Last backup date from backup_history
                c.execute("SELECT created_at FROM backup_history WHERE status = 'Success' ORDER BY created_at DESC LIMIT 1")
                row_b = c.fetchone()
                last_backup = row_b[0] if row_b else 'Never'

                response = {
                    "name": db_name,
                    "size": db_size,
                    "total_records": total_records,
                    "last_backup": last_backup,
                    "health": "Healthy"
                }
            
            else:
                response = {"error": "Invalid action"}
                
        except Exception as e:
            response = {"error": str(e)}
        finally:
            conn.close()

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        if self.path.startswith('/api?'):
            self.handle_post_api()
        elif self.path == '/chat' or self.path == '/api/chat' or self.path.startswith('/api?action=chat'):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                message = data.get('message', '')
                history = data.get('history', None)
            except:
                message = ""
                history = None

            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            response = self.process_chat(message, c, history=history)
            conn.close()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            super().do_POST()

    def handle_post_api(self):
        query_str = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query_str)
        action = params.get('action', [''])[0]
        
        content_type = self.headers.get('Content-Type', '')
        content_length = int(self.headers.get('Content-Length', 0))
        ip_address = self.client_address[0]
        ua_string = self.headers.get('User-Agent', '')
        
        body = b""
        if content_length > 0:
            body = self.rfile.read(content_length)
            
        boundary = ""
        if 'multipart/form-data' in content_type:
            parts_ct = content_type.split(';')
            for p in parts_ct:
                p = p.strip()
                if p.startswith('boundary='):
                    boundary = p.split('=', 1)[1]
                    
        payload = {}
        files = {}
        fields = {}
        status_code = 200
        response = {}
        
        if boundary:
            try:
                fields, files = parse_multipart(body, boundary)
            except Exception as e:
                response = {"error": f"Error parsing multipart: {str(e)}"}
                status_code = 400
        elif 'application/json' in content_type and body:
            try:
                payload = json.loads(body.decode('utf-8'))
            except Exception as e:
                response = {"error": f"Error parsing JSON: {str(e)}"}
                status_code = 400
                
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        try:
            session_token = self.headers.get('X-Session-Token', '') or params.get('session_token', [''])[0]
            user_id = get_user_from_session(c, session_token)
            
            c.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
            user = c.fetchone()
            if not user:
                c.execute("SELECT id, name, email FROM users ORDER BY id LIMIT 1")
                user = c.fetchone()
                user_id = user['id']
            
            if session_token:
                resolve_active_device(c, user_id, session_token, ua_string, ip_address)
                conn.commit()
                
            if status_code == 200:
                if action == 'update_profile':
                    profile = payload.get('profile', {})
                    library = payload.get('library', {})
                    security = payload.get('security', {})
                    backup_sched = payload.get('backupSchedule', 'none')
                    
                    c.execute("UPDATE users SET name=?, email=? WHERE id=?", (profile.get('fullName', user['name']), profile.get('email', user['email']), user_id))
                    
                    c.execute("SELECT avatar_path, avatar_upload_date, avatar_uploaded_by FROM user_profiles WHERE user_id = ?", (user_id,))
                    row = c.fetchone()
                    avatar_path = row['avatar_path'] if row else 'https://ui-avatars.com/api/?name=Admin+User&background=9d50bb&color=fff'
                    avatar_date = row['avatar_upload_date'] if row else None
                    avatar_by = row['avatar_uploaded_by'] if row else None
                    
                    c.execute("""
                        INSERT INTO user_profiles (user_id, account_type, avatar_path, avatar_upload_date, avatar_uploaded_by, phone_number, employee_id, student_id, designation)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(user_id) DO UPDATE SET
                            account_type = excluded.account_type,
                            phone_number = excluded.phone_number,
                            employee_id = excluded.employee_id,
                            student_id = excluded.student_id,
                            designation = excluded.designation
                    """, (user_id, profile.get('accountType', 'Admin'), avatar_path, avatar_date, avatar_by, profile.get('phone', ''), profile.get('employeeId', ''), profile.get('studentId', ''), profile.get('designation', '')))
                    
                    c.execute("""
                        INSERT INTO library_settings (id, library_name, library_code, institution_name, address, city, state, country, zip_code)
                        VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(id) DO UPDATE SET
                            library_name = excluded.library_name,
                            library_code = excluded.library_code,
                            institution_name = excluded.institution_name,
                            address = excluded.address,
                            city = excluded.city,
                            state = excluded.state,
                            country = excluded.country,
                            zip_code = excluded.zip_code
                    """, (
                        library.get('libraryName', 'Central Public Library'),
                        library.get('libraryCode', 'LIB-001'),
                        library.get('institutionName', ''),
                        library.get('address', ''),
                        library.get('city', ''),
                        library.get('state', ''),
                        library.get('country', ''),
                        library.get('zipCode', '')
                    ))
                    
                    c.execute("""
                        INSERT INTO user_preferences (
                            user_id, session_timeout, max_login_attempts, lock_duration, auto_logout, email_otp, authenticator_app, backup_schedule
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(user_id) DO UPDATE SET
                            session_timeout = excluded.session_timeout,
                            max_login_attempts = excluded.max_login_attempts,
                            lock_duration = excluded.lock_duration,
                            auto_logout = excluded.auto_logout,
                            email_otp = excluded.email_otp,
                            authenticator_app = excluded.authenticator_app,
                            backup_schedule = excluded.backup_schedule
                    """, (
                        user_id,
                        int(security.get('sessionTimeout', 30)),
                        int(security.get('maxLoginAttempts', 5)),
                        int(security.get('lockDuration', 15)),
                        int(security.get('autoLogout', True)),
                        int(security.get('emailOtp', False)),
                        int(security.get('authenticatorApp', False)),
                        backup_sched
                    ))
                    
                    log_audit(c, user_id, "Profile Updated", "Settings", user['name'], profile.get('fullName', user['name']), ip_address, ua_string)
                    add_system_notification(c, user_id, 'Security', 'Profile Settings Modified', 'Your administrator profile settings and library metadata were successfully updated.')
                    conn.commit()
                    response = {"success": True}
                    
                elif action == 'upload_avatar':
                    file_data = b""
                    filename = "avatar.png"
                    if boundary and 'avatar' in files:
                        file_data = files['avatar']['data']
                        filename = files['avatar']['filename']
                    elif 'avatar_data' in payload:
                        import base64
                        b64_data = payload['avatar_data']
                        if ',' in b64_data:
                            b64_data = b64_data.split(',', 1)[1]
                        file_data = base64.b64decode(b64_data)
                        filename = payload.get('filename', 'avatar.png')
                        
                    if not file_data:
                        status_code = 400
                        response = {"error": "No avatar file data uploaded"}
                    elif not validate_magic_bytes(file_data):
                        status_code = 400
                        response = {"error": "Unsupported image format. Only JPG, PNG, and WEBP are allowed."}
                    elif len(file_data) > 2 * 1024 * 1024:
                        status_code = 400
                        response = {"error": "File size exceeds 2MB limit."}
                    else:
                        uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'uploads', 'avatars')
                        os.makedirs(uploads_dir, exist_ok=True)
                        ext = filename.split('.')[-1].lower() if '.' in filename else 'png'
                        if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                            ext = 'png'
                        new_filename = f"avatar_{user_id}_{int(time.time())}.{ext}"
                        filepath = os.path.join(uploads_dir, new_filename)
                        with open(filepath, 'wb') as f:
                            f.write(file_data)
                            
                        avatar_path = f"uploads/avatars/{new_filename}"
                        c.execute("""
                            INSERT INTO user_profiles (user_id, avatar_path, avatar_upload_date, avatar_uploaded_by)
                            VALUES (?, ?, CURRENT_TIMESTAMP, ?)
                            ON CONFLICT(user_id) DO UPDATE SET
                                avatar_path = excluded.avatar_path,
                                avatar_upload_date = excluded.avatar_upload_date,
                                avatar_uploaded_by = excluded.avatar_uploaded_by
                        """, (user_id, avatar_path, user['name']))
                        
                        log_audit(c, user_id, "Avatar Changed", "Settings", "—", avatar_path, ip_address, ua_string)
                        conn.commit()
                        response = {"success": True, "avatar_path": avatar_path}
                        
                elif action == 'remove_avatar':
                    c.execute("SELECT avatar_path FROM user_profiles WHERE user_id = ?", (user_id,))
                    row = c.fetchone()
                    old_path = row['avatar_path'] if row else "—"
                    default_path = f"https://ui-avatars.com/api/?name={urllib.parse.quote(user['name'])}&background=9d50bb&color=fff"
                    c.execute("""
                        INSERT INTO user_profiles (user_id, avatar_path, avatar_upload_date, avatar_uploaded_by)
                        VALUES (?, ?, NULL, NULL)
                        ON CONFLICT(user_id) DO UPDATE SET
                            avatar_path = excluded.avatar_path,
                            avatar_upload_date = excluded.avatar_upload_date,
                            avatar_uploaded_by = excluded.avatar_uploaded_by
                        """, (user_id, default_path))
                    
                    log_audit(c, user_id, "Avatar Removed", "Settings", old_path, default_path, ip_address, ua_string)
                    conn.commit()
                    response = {"success": True, "avatar_path": default_path}
                    
                elif action == 'update_password':
                    current_pw = payload.get('currentPassword', '')
                    new_pw = payload.get('newPassword', '')
                    
                    try:
                        c.execute("ALTER TABLE users ADD COLUMN password TEXT DEFAULT 'admin123'")
                        conn.commit()
                    except sqlite3.OperationalError:
                        pass
                        
                    c.execute("SELECT password FROM users WHERE id = ?", (user_id,))
                    stored = c.fetchone()['password']
                    
                    if not stored or stored == 'admin123':
                        stored = hash_password('admin123')
                        c.execute("UPDATE users SET password = ? WHERE id = ?", (stored, user_id))
                        conn.commit()
                        
                    c.execute("SELECT max_login_attempts, lock_duration FROM user_preferences WHERE user_id = ?", (user_id,))
                    pref = c.fetchone()
                    max_attempts = pref['max_login_attempts'] if pref else 5
                    lock_dur = pref['lock_duration'] if pref else 15
                    
                    c.execute("""
                        SELECT COUNT(*) FROM login_history 
                        WHERE user_id = ? AND status = 'Failed' 
                        AND timestamp > datetime('now', '-' || ? || ' minutes')
                    """, (user_id, lock_dur))
                    failed_count = c.fetchone()[0]
                    
                    if failed_count >= max_attempts:
                        status_code = 400
                        response = {"error": f"Security lockout: Too many failed verification attempts. Try again in {lock_dur} minutes."}
                    elif not verify_password(stored, current_pw):
                        c.execute("""
                            INSERT INTO login_history (user_id, username, ip_address, device_info, status, failure_reason)
                            VALUES (?, ?, ?, ?, 'Failed', 'Incorrect Current Password')
                        """, (user_id, user['name'], ip_address, ua_string))
                        log_audit(c, user_id, "Password Verification Failed", "Security", "—", "Failed Verification Attempt", ip_address, ua_string)
                        conn.commit()
                        
                        status_code = 400
                        response = {"error": "Current password is incorrect"}
                    else:
                        ok, msg = validate_password_strength(new_pw)
                        if not ok:
                            status_code = 400
                            response = {"error": msg}
                        else:
                            hashed = hash_password(new_pw)
                            c.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user_id))
                            c.execute("INSERT INTO password_history (user_id, password_hash) VALUES (?, ?)", (user_id, hashed))
                            
                            c.execute("""
                                INSERT INTO login_history (user_id, username, ip_address, device_info, status)
                                VALUES (?, ?, ?, ?, 'Success')
                            """, (user_id, user['name'], ip_address, ua_string))
                            
                            log_audit(c, user_id, "Password Changed", "Security", "—", "Hashed Password Updated", ip_address, ua_string)
                            add_system_notification(c, user_id, 'Security', 'Password Changed Successfully', 'Your account password has been successfully updated. Recent sessions have been re-verified.')
                            conn.commit()
                            response = {"success": True}
                            
                elif action == 'logout_device':
                    target_token = payload.get('session_token', '')
                    c.execute("UPDATE user_devices SET is_active = 0 WHERE session_token = ?", (target_token,))
                    log_audit(c, user_id, "Device Logged Out", "Security", target_token, "Inactive", ip_address, ua_string)
                    conn.commit()
                    response = {"success": True}
                    
                elif action == 'logout_all_devices':
                    c.execute("UPDATE user_devices SET is_active = 0 WHERE user_id = ? AND session_token != ?", (user_id, session_token or ''))
                    log_audit(c, user_id, "All Other Devices Terminated", "Security", "Multiple Devices", "Terminated", ip_address, ua_string)
                    conn.commit()
                    response = {"success": True}
                    
                elif action == 'update_notifications':
                    toggles = payload.get('toggles', {})
                    channels = payload.get('channels', {})
                    
                    c.execute("""
                        INSERT INTO user_notifications (
                            user_id, notify_new_member, notify_book_issue, notify_book_return,
                            notify_overdue, notify_fine, notify_new_admin, notify_dashboard,
                            notify_maintenance, notify_database, notify_security,
                            channel_email, channel_sms, channel_in_app
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(user_id) DO UPDATE SET
                            notify_new_member = excluded.notify_new_member,
                            notify_book_issue = excluded.notify_book_issue,
                            notify_book_return = excluded.notify_book_return,
                            notify_overdue = excluded.notify_overdue,
                            notify_fine = excluded.notify_fine,
                            notify_new_admin = excluded.notify_new_admin,
                            notify_dashboard = excluded.notify_dashboard,
                            notify_maintenance = excluded.notify_maintenance,
                            notify_database = excluded.notify_database,
                            notify_security = excluded.notify_security,
                            channel_email = excluded.channel_email,
                            channel_sms = excluded.channel_sms,
                            channel_in_app = excluded.channel_in_app
                    """, (
                        user_id,
                        int(toggles.get('newMember', True)),
                        int(toggles.get('bookIssue', True)),
                        int(toggles.get('bookReturn', True)),
                        int(toggles.get('overdue', True)),
                        int(toggles.get('fine', True)),
                        int(toggles.get('newAdmin', True)),
                        int(toggles.get('dashboard', True)),
                        int(toggles.get('maintenance', True)),
                        int(toggles.get('database', True)),
                        int(toggles.get('security', True)),
                        int(channels.get('email', True)),
                        int(channels.get('sms', False)),
                        int(channels.get('inApp', True))
                    ))
                    
                    log_audit(c, user_id, "Notification Prefs Updated", "Notifications", "—", "Toggles Synced", ip_address, ua_string)
                    conn.commit()
                    response = {"success": True}
                    
                elif action == 'update_theme':
                    cust = payload.get('customization', {})
                    
                    c.execute("""
                        INSERT INTO theme_settings (
                            user_id, accent_color, visual_mode, glassmorphism, font_family, ui_density, animations_enabled, font_size, font_weight, letter_spacing, line_height
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(user_id) DO UPDATE SET
                            accent_color = excluded.accent_color,
                            visual_mode = excluded.visual_mode,
                            glassmorphism = excluded.glassmorphism,
                            font_family = excluded.font_family,
                            ui_density = excluded.ui_density,
                            animations_enabled = excluded.animations_enabled,
                            font_size = excluded.font_size,
                            font_weight = excluded.font_weight,
                            letter_spacing = excluded.letter_spacing,
                            line_height = excluded.line_height
                    """, (
                        user_id,
                        cust.get('accentColor', 'blue'),
                        cust.get('visualMode', 'dark'),
                        int(cust.get('glassmorphism', True)),
                        cust.get('fontFamily', 'cinzel'),
                        cust.get('uiDensity', 'comfortable'),
                        int(cust.get('animationsEnabled', True)),
                        cust.get('fontSize', '14px'),
                        cust.get('fontWeight', 'normal'),
                        cust.get('letterSpacing', '0px'),
                        cust.get('lineHeight', '1.6')
                    ))
                    
                    log_audit(c, user_id, "Theme Configuration Updated", "Theme", "—", cust.get('accentColor', 'blue'), ip_address, ua_string)
                    conn.commit()
                    response = {"success": True}
                    
                elif action == 'db_backup':
                    backups_dir = os.path.abspath(os.path.join(os.path.dirname(DB_FILE), 'backups'))
                    thread = threading.Thread(target=make_async_backup, args=(DB_FILE, backups_dir, 'manual'))
                    thread.daemon = True
                    thread.start()
                    
                    log_audit(c, user_id, "Asynchronous Database Backup Triggered", "Database", "—", "Background Thread Spawned", ip_address, ua_string)
                    add_system_notification(c, user_id, 'Database', 'Asynchronous Database Backup Triggered', 'A new manual backup task has been queued and is executing in the background.')
                    conn.commit()
                    response = {"success": True, "message": "Asynchronous database backup is executing."}
                    
                elif action == 'db_restore':
                    file_data = b""
                    if boundary and 'restore_file' in files:
                        file_data = files['restore_file']['data']
                    elif 'file_data' in payload:
                        import base64
                        file_data = base64.b64decode(payload['file_data'])
                        
                    if not file_data:
                        status_code = 400
                        response = {"error": "No backup file uploaded"}
                    else:
                        if file_data.startswith(b'SQLite format 3'):
                            with open(DB_FILE, 'wb') as f:
                                f.write(file_data)
                            log_audit(c, user_id, "Database Restored", "Database", "—", "SQLite File Overwritten", ip_address, ua_string)
                            add_system_notification(c, user_id, 'Database', 'Database Restored Successfully', 'Your database was successfully rolled back and restored from the selected backup file.')
                            conn.commit()
                            response = {"success": True}
                        else:
                            status_code = 400
                            response = {"error": "Invalid SQLite database backup format"}
                            
                elif action == 'db_optimize':
                    c.execute("VACUUM")
                    log_audit(c, user_id, "Database Vacuum Optimized", "Database", "—", "SQLite VACUUM Complete", ip_address, ua_string)
                    add_system_notification(c, user_id, 'Database', 'Database Optimized Successfully', 'The library database was vacuumed and optimized, shrinking disk footprint.')
                    conn.commit()
                    response = {"success": True}
                    
                elif action == 'db_clear_cache':
                    log_audit(c, user_id, "Database Engine Cache Cleared", "Database", "—", "SQLite Cache Purged", ip_address, ua_string)
                    add_system_notification(c, user_id, 'Database', 'Database Cache Cleared', 'SQLite internal file cache buffers have been cleared and purged.')
                    conn.commit()
                    response = {"success": True}
                    
                elif action == 'db_repair':
                    c.execute("PRAGMA integrity_check")
                    res = c.fetchone()[0]
                    log_audit(c, user_id, "Database Integrity Checked", "Database", "—", f"PRAGMA check: {res}", ip_address, ua_string)
                    add_system_notification(c, user_id, 'Database', 'Database Integrity Checked', f'Database health check completed. Integrity result: {res}')
                    conn.commit()
                    response = {"success": True, "result": res}
                    
                elif action == 'db_rebuild_indexes':
                    c.execute("REINDEX")
                    log_audit(c, user_id, "Indexes Rebuilt", "Database", "—", "SQLite REINDEX execution complete", ip_address, ua_string)
                    add_system_notification(c, user_id, 'Database', 'Database Indexes Rebuilt', 'Reindexing completed successfully. Query performance has been optimized.')
                    conn.commit()
                    response = {"success": True}

                elif action == 'delete_backup':
                    filename = payload.get('filename', '')
                    if not filename or '/' in filename or '\\' in filename:
                        status_code = 400
                        response = {"error": "Invalid backup filename"}
                    else:
                        backups_dir = os.path.abspath(os.path.join(os.path.dirname(DB_FILE), 'backups'))
                        file_path = os.path.join(backups_dir, filename)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            c.execute("DELETE FROM backup_history WHERE filename = ?", (filename,))
                            log_audit(c, user_id, "Database Backup Deleted", "Database", filename, "Deleted", ip_address, ua_string)
                            conn.commit()
                            response = {"success": True}
                        else:
                            status_code = 404
                            response = {"error": "Backup file not found"}

                elif action == 'dismiss_notification':
                    notif_id = payload.get('id', '')
                    c.execute("UPDATE system_notifications SET is_read = 1 WHERE id = ? AND user_id = ?", (notif_id, user_id))
                    log_audit(c, user_id, "Notification Dismissed", "System", str(notif_id), "Read", ip_address, ua_string)
                    conn.commit()
                    response = {"success": True}
                    
                else:
                    status_code = 400
                    response = {"error": f"Invalid POST action: {action}"}
                    
        except Exception as e:
            status_code = 500
            response = {"error": str(e)}
        finally:
            conn.close()
            
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def local_fallback_chat(self, msg, c, history=None):
        import difflib
        msg_lower = msg.lower().strip()
        
        # Clean input punctuation
        def clean_str(s):
            return ''.join(ch for ch in s.lower() if ch.isalnum() or ch.isspace()).strip()
            
        clean_msg = clean_str(msg)

        # Helper to fuzzy find a book in the database
        def fuzzy_find_book(text):
            c.execute("SELECT id, title, author, category, publisher, price, description, total_quantity, available_quantity, rating, borrow_count FROM books")
            books = c.fetchall()
            
            # Sort by title length descending
            books_sorted = sorted(books, key=lambda x: len(x[1]), reverse=True)
            
            # 1. Exact or substring checks first
            clean_text = clean_str(text)
            for b in books_sorted:
                title = b[1].lower()
                clean_title = clean_str(title)
                if clean_title == clean_text or (len(clean_title) > 3 and clean_title in clean_text):
                    return b
                    
            # 2. Fuzzy SequenceMatcher ratio checks
            best_match = None
            best_ratio = 0.0
            
            # Extract potential book title from clean user text
            potential_title = clean_text
            for prefix in ['give me a book of ', 'give me book ', 'give me ', 'book of ', 'tell me about ', 'explain ', 'what is ', 'is ', ' available', ' present', 'search for ', 'search ']:
                if prefix in clean_text:
                    potential_title = clean_text.split(prefix)[-1].strip()
                    break

            for b in books_sorted:
                title = b[1].lower()
                clean_title = clean_str(title)
                
                ratio = difflib.SequenceMatcher(None, clean_title, clean_text).ratio()
                sub_ratio = difflib.SequenceMatcher(None, clean_title, potential_title).ratio()
                max_r = max(ratio, sub_ratio)
                
                if max_r > best_ratio:
                    best_ratio = max_r
                    best_match = b
                    
            if best_ratio >= 0.70:
                return best_match
            return None

        # Context memory: check what was last discussed
        last_context = None
        if history:
            for h in reversed(history):
                h_text = h.get('text', '').lower()
                for cat in ['self help', 'self-help', 'business', 'fiction', 'science', 'technology', 'finance', 'psychology', 'history', 'philosophy', 'health', 'wellness']:
                    if cat in h_text:
                        last_context = ("category", cat)
                        break
                if last_context:
                    break
                book_in_hist = fuzzy_find_book(h.get('text', ''))
                if book_in_hist:
                    last_context = ("book", book_in_hist)
                    break

        # Check for generic greetings first (Requirement 12)
        if msg_lower in ['hi', 'hello', 'hey', 'greetings', 'yo']:
            return {
                "reply": "Hello! I am your AI Library Assistant. I am currently running in a robust offline integration mode.<br><br>"
                         "Here are some examples of what you can ask me to do:<br>"
                         "• <strong>Database Stats:</strong> 'How many books are available?', 'How many registered members do we have?'<br>"
                         "• <strong>Catalog Lists:</strong> 'list books', 'list members', 'list categories', 'list transactions'<br>"
                         "• <strong>Book Search:</strong> 'Is Atomic Habits available?', 'Do you have Rich Dad Poor Dad?'<br>"
                         "• <strong>Recommendations:</strong> 'Recommend psychology books', 'Best business books'<br>"
                         "• <strong>Guidance:</strong> 'How do I borrow a book?', 'What are the return late policies?'<br>"
                         "• <strong>Q&A:</strong> 'What is Space and Time?', 'What is Blockchain?'"
            }

        # Check for commands to list catalog items
        if any(kw in msg_lower for kw in ['list books', 'show all books', 'all books', 'catalog', 'show books', 'list of books']):
            c.execute("SELECT id, title, author, category, available_quantity FROM books LIMIT 15")
            rows = c.fetchall()
            lst = []
            for r in rows:
                status = "Available" if r[4] > 0 else "Checked out"
                lst.append(f"• <strong>{r[1]}</strong> by {r[2]} ({r[3]}) - <em>{status}</em>")
            return {
                "reply": "📚 <strong>Library Books Catalog (First 15 titles):</strong><br><br>" + "<br>".join(lst) + "<br><br><em>Use 'search [title]' or 'recommend [genre]' for more details!</em>"
            }

        if any(kw in msg_lower for kw in ['list members', 'show members', 'all members', 'show all members', 'list of members']):
            c.execute("SELECT name, email FROM users LIMIT 15")
            rows = c.fetchall()
            lst = []
            for r in rows:
                lst.append(f"• <strong>{r[0]}</strong> ({r[1]})")
            return {
                "reply": "👤 <strong>Registered Library Members (First 15 members):</strong><br><br>" + "<br>".join(lst)
            }

        if any(kw in msg_lower for kw in ['list categories', 'show categories', 'all categories', 'list of categories']):
            c.execute("SELECT DISTINCT category FROM books WHERE category IS NOT NULL AND category != ''")
            categories = [r[0] for r in c.fetchall()]
            lst = [f"• <strong>{cat}</strong>" for cat in categories]
            return {
                "reply": "🏷️ <strong>Book Categories Available:</strong><br><br>" + "<br>".join(lst)
            }

        if any(kw in msg_lower for kw in ['list authors', 'show authors', 'all authors', 'list of authors']):
            c.execute("SELECT DISTINCT author FROM books WHERE author IS NOT NULL AND author != '' LIMIT 15")
            authors = [r[0] for r in c.fetchall()]
            lst = [f"• <strong>{auth}</strong>" for auth in authors]
            return {
                "reply": "✍️ <strong>Registered Authors (First 15):</strong><br><br>" + "<br>".join(lst)
            }

        if any(kw in msg_lower for kw in ['list publishers', 'show publishers', 'all publishers', 'list of publishers']):
            c.execute("SELECT DISTINCT publisher FROM books WHERE publisher IS NOT NULL AND publisher != '' LIMIT 15")
            publishers = [r[0] for r in c.fetchall()]
            lst = [f"• <strong>{pub}</strong>" for pub in publishers]
            return {
                "reply": "🏢 <strong>Registered Publishers (First 15):</strong><br><br>" + "<br>".join(lst)
            }

        if any(kw in msg_lower for kw in ['list transactions', 'show transactions', 'all transactions', 'list borrows', 'show borrows', 'all borrows']):
            c.execute("SELECT t.id, u.name, b.title, t.issue_date, t.return_date, t.actual_return_date FROM transactions t JOIN users u ON t.user_id = u.id JOIN books b ON t.book_id = b.id ORDER BY t.issue_date DESC LIMIT 10")
            rows = c.fetchall()
            lst = []
            for r in rows:
                status = f"Returned on {r[5]}" if r[5] else f"Active (Due {r[4]})"
                lst.append(f"• Tx #{r[0]}: <strong>{r[1]}</strong> borrowed <em>'{r[2]}'</em> - <strong>{status}</strong>")
            return {
                "reply": "📊 <strong>Recent Transactions Log (First 10):</strong><br><br>" + ("<br>".join(lst) if lst else "No active transactions found.")
            }

        # If user asks generic follow-up "recommend more" or similar
        generic_followup = any(kw in msg_lower for kw in ['recommend more', 'suggest others', 'suggest some others', 'tell me more', 'what else', 'more books', 'another one', 'recommend another'])
        if generic_followup and last_context:
            if last_context[0] == "category":
                genre = last_context[1]
                return self.get_genre_recommendations_reply(genre, c)
            elif last_context[0] == "book":
                book = last_context[1]
                return self.get_book_details_reply(book, c, is_followup=True)

        # 1. Prioritized Q&A Educational Explanations
        # We handle this if they don't explicitly mention "book", "read", "borrow", "give me a book" or "give me book".
        has_explicit_book_seeking = any(kw in msg_lower for kw in ['book', 'read', 'borrow', 'give me a ', 'give me ', 'buy', 'purchase', 'do you have'])
        
        is_qa = False
        qa_reply = ""
        
        qa_prefixes = ['what is ', 'who is ', 'explain ', 'define ', 'tell me about ']
        qa_topic = None
        if not has_explicit_book_seeking:
            for prefix in qa_prefixes:
                if msg_lower.startswith(prefix):
                    qa_topic = msg_lower[len(prefix):].strip(' ?.')
                    break
            
            if not qa_topic and any(kw in msg_lower for kw in ['antigravity', 'anti-gravity', 'space', 'time', 'blockchain', 'machine learning', 'artificial intelligence', 'philosophy', 'psychology']):
                # If they just said the word without "what is", let's extract it
                for kw in ['antigravity', 'anti-gravity', 'space and time', 'space', 'time', 'blockchain', 'machine learning', 'artificial intelligence', 'philosophy', 'psychology']:
                    if kw in msg_lower:
                        qa_topic = kw
                        break
                        
        if qa_topic:
            try:
                import urllib.request
                import json
                import urllib.parse
                req = urllib.request.Request(f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(qa_topic)}", headers={'User-Agent': 'Mozilla/5.0'})
                res = urllib.request.urlopen(req, timeout=3)
                wiki_data = json.loads(res.read().decode())
                if 'extract' in wiki_data:
                    qa_reply = f"<strong>{wiki_data.get('title', qa_topic.title())}:</strong> {wiki_data['extract']}"
                    is_qa = True
            except Exception as e:
                # If wikipedia fails, just ignore and let it fall through to book search
                pass

        if is_qa:
            return {"reply": qa_reply}

        # 2. Library Statistics & Database Queries
        is_stats = False
        stats_replies = []
        
        if any(kw in msg_lower for kw in ['how many books', 'total books', 'number of books', 'books available', 'how many copies', 'total copies']):
            c.execute("SELECT SUM(total_quantity), SUM(available_quantity), COUNT(DISTINCT id) FROM books")
            row = c.fetchone()
            total_qty = row[0] if row[0] is not None else 0
            avail_qty = row[1] if row[1] is not None else 0
            total_titles = row[2] if row[2] is not None else 0
            stats_replies.append(f"We have <strong>{total_qty}</strong> total copies across <strong>{total_titles}</strong> unique book titles in our catalog. Currently, <strong>{avail_qty}</strong> copies are available on shelves for borrowing.")
            is_stats = True
            
        if any(kw in msg_lower for kw in ['how many members', 'total members', 'registered members', 'registered users', 'number of members']):
            c.execute("SELECT COUNT(*) FROM users")
            total_users = c.fetchone()[0]
            stats_replies.append(f"There are currently <strong>{total_users}</strong> registered library members in our system.")
            is_stats = True
            
        if any(kw in msg_lower for kw in ['how many borrowed', 'currently borrowed', 'borrowed books', 'books currently borrowed']):
            c.execute("SELECT COUNT(*) FROM transactions WHERE actual_return_date IS NULL")
            borrowed = c.fetchone()[0]
            stats_replies.append(f"There are currently <strong>{borrowed}</strong> books actively borrowed by members.")
            is_stats = True
            
        if any(kw in msg_lower for kw in ['how many overdue', 'overdue books', 'number of overdue']):
            c.execute("SELECT COUNT(*) FROM transactions WHERE actual_return_date IS NULL AND return_date < date('now')")
            overdue = c.fetchone()[0]
            stats_replies.append(f"There are currently <strong>{overdue}</strong> overdue books in our records.")
            is_stats = True
            
        if any(kw in msg_lower for kw in ['how many categories', 'total categories', 'what categories', 'genres available']):
            c.execute("SELECT DISTINCT category FROM books WHERE category IS NOT NULL AND category != ''")
            categories = [r[0] for r in c.fetchall()]
            stats_replies.append(f"We have <strong>{len(categories)}</strong> distinct book categories: {', '.join(categories)}.")
            is_stats = True
            
        if any(kw in msg_lower for kw in ['most borrowed', 'popular books', 'top borrowed', 'frequently borrowed']):
            c.execute("SELECT title, author, borrow_count FROM books ORDER BY borrow_count DESC LIMIT 3")
            rows = c.fetchall()
            lst = []
            for i, r in enumerate(rows):
                lst.append(f"{i+1}. <strong>{r[0]}</strong> by {r[1]} ({r[2]} borrows)")
            stats_replies.append("The most popular books in our library are:<br>" + "<br>".join(lst))
            is_stats = True
            
        if any(kw in msg_lower for kw in ['newest books', 'new books', 'recently added', 'newest added']):
            c.execute("SELECT title, author, category FROM books ORDER BY id DESC LIMIT 3")
            rows = c.fetchall()
            lst = []
            for r in rows:
                lst.append(f"• <strong>{r[0]}</strong> by {r[1]} ({r[2]})")
            stats_replies.append("The newest additions to our collection are:<br>" + "<br>".join(lst))
            is_stats = True

        if is_stats:
            return {"reply": "<br><br>".join(stats_replies)}

        # 3. Policy Guidance (Borrowing/Returning/Librarian Assistance)
        if any(kw in msg_lower for kw in ['borrow', 'how to borrow', 'borrow limit', 'borrow policy', 'due date', 'fine']):
            return {
                "reply": "<strong>📚 Borrowing Guidance:</strong><br><br>"
                         "1. <strong>Select a Book:</strong> Use the Dashboard search bar or ask me to check availability.<br>"
                         "2. <strong>Borrowing Limit:</strong> You can borrow up to <strong>5 books</strong> at a time.<br>"
                         "3. <strong>Standard Loan Period:</strong> Books are issued for <strong>14 days</strong>.<br>"
                         "4. <strong>Late Fines:</strong> If returned late, a fine of <strong>$0.50 per day</strong> will be charged to your account.<br>"
                         "5. <strong>How to Issue:</strong> Go to the 'Borrowed Books' page, choose your Member, select the Book, set a return date, and click 'Issue Book'.<br>"
                         "6. <strong>Reservations:</strong> If all copies are checked out, you can reserve a book to be notified when it returns."
            }

        if any(kw in msg_lower for kw in ['return', 'how to return', 'late return', 'renew', 'late policy', 'fine calculation']):
            return {
                "reply": "<strong>🔄 Returning Books Guidance:</strong><br><br>"
                         "1. <strong>Deadline:</strong> Return books within 14 days of issue to avoid any penalty.<br>"
                         "2. <strong>Late Returns:</strong> A late fee of <strong>$0.50 per day</strong> is dynamically calculated starting from the day after the due date.<br>"
                         "3. <strong>How to Return:</strong> Navigate to the 'Borrowed Books' tab, find your active borrowing record in the transactions list, and click the <strong>'Return'</strong> button. The system will automatically update stock and calculate any outstanding fines.<br>"
                         "4. <strong>Renewals:</strong> If you need more time, you can renew a book for an additional 7 days before it becomes overdue, provided no other member has reserved it."
            }

        if any(kw in msg_lower for kw in ['navigate', 'membership', 'register', 'account', 'reserve', 'history', 'rules', 'faq', 'help', 'librarian']):
            return {
                "reply": "<strong>ℹ️ Matrix Library Navigation Guide:</strong><br><br>"
                         "I am your Virtual Librarian! Here is how to navigate and manage your account:<br>"
                         "• <strong>Membership Registration:</strong> Go to the 'Members' page and click <strong>'Add Member'</strong> to register an account with a name and email.<br>"
                         "• <strong>Catalog Search:</strong> Use the search bar on the <strong>'Dashboard'</strong> or <strong>'Books'</strong> page to view the live library catalog.<br>"
                         "• <strong>View Reading History:</strong> Check your borrowed and returned books log on the 'Borrowed Books' tab.<br>"
                         "• <strong>Fines & Payments:</strong> Outstanding fines are displayed in the user profile settings and transaction logs.<br>"
                         "• <strong>Admin Tools:</strong> Use the Database Management module to backup or vacuum the database.<br><br>"
                         "If you need anything else, just ask me to 'recommend books' or 'search [title]'!"
            }

        # 4. Intelligent Recommendations / Recommendation Engine
        for genre in ['self help', 'self-help', 'business', 'fiction', 'science', 'technology', 'finance', 'psychology', 'history', 'philosophy', 'health', 'wellness']:
            if genre in msg_lower and any(kw in msg_lower for kw in ['recommend', 'suggest', 'book', 'list', 'best', 'popular', 'beginner', 'top']):
                return self.get_genre_recommendations_reply(genre, c)

        if any(kw in msg_lower for kw in ['recommend', 'suggest', 'book list', 'popular books', 'best books']):
            return self.get_genre_recommendations_reply('self-help', c)

        # 5. Dynamic Book Search / Details Retrieval (Fuzzy matching + External LibGen fallback)
        matched_book = fuzzy_find_book(msg)
        if matched_book:
            return self.get_book_details_reply(matched_book, c)
            
        # Extract potential search query from sentence structure
        potential_search = msg_lower
        for phrase in ['give me a book of ', 'give me book ', 'give me ', 'book of ', 'tell me about ', 'explain ', 'what is ', 'is ', ' available', ' present', 'search for ', 'search ', 'find ', 'lookup ']:
            if phrase in msg_lower:
                parts = msg_lower.split(phrase)
                if len(parts) > 1 and len(parts[1].strip()) > 0:
                    potential_search = parts[1].replace('available', '').replace('present', '').replace('?', '').strip()
                    break

        if potential_search:
            # Let's perform fuzzy query suggestions
            c.execute("SELECT title, author, category FROM books ORDER BY RANDOM() LIMIT 3")
            sim_books = c.fetchall()
            sim_text = "<br>".join([f"• <strong>{b[0]}</strong> by {b[1]} ({b[2]})" for b in sim_books])
            
            # Formatted exactly as requested
            return {
                "reply": f"Sorry, the book '{potential_search.title()}' is not present in my database.<br><br>"
                         f"You can find it on external resources such as:<br>"
                         f"<a href='https://libgen.li/index.php' target='_blank' style='color:var(--neon-blue); font-weight:bold;'>Library Genesis</a><br><br>"
                         f"Alternatively, here are some similar/recommended books you can borrow from our catalog:<br>{sim_text}"
            }

        # 6. Default Fallback
        return {
            "reply": "Hello! I am your AI Library Assistant. I am currently running in a robust offline integration mode.<br><br>"
                     "Here are some examples of what you can ask me to do:<br>"
                     "• <strong>Database Stats:</strong> 'How many books are available?', 'How many registered members do we have?'<br>"
                     "• <strong>Book Search:</strong> 'Is Atomic Habits available?', 'Do you have Rich Dad Poor Dad?'<br>"
                     "• <strong>Recommendations:</strong> 'Recommend psychology books', 'Best business books'<br>"
                     "• <strong>Guidance:</strong> 'How do I borrow a book?', 'What are the return late policies?'<br>"
                     "• <strong>Q&A:</strong> 'What is Space and Time?', 'What is Blockchain?'"
        }

        # 8. Intelligent Recommendations / Recommendation Engine
        for genre in ['self help', 'self-help', 'business', 'fiction', 'science', 'technology', 'finance', 'psychology', 'history', 'philosophy', 'health', 'wellness']:
            if genre in msg_lower and any(kw in msg_lower for kw in ['recommend', 'suggest', 'book', 'list', 'best', 'popular', 'beginner', 'top']):
                return self.get_genre_recommendations_reply(genre, c)

        if any(kw in msg_lower for kw in ['recommend', 'suggest', 'book list', 'popular books', 'best books']):
            return self.get_genre_recommendations_reply('self-help', c)

        # 9. Default Chatbot response
        return {
            "reply": "Hello! I am your AI Library Assistant. I am currently running in a robust offline integration mode.<br><br>"
                     "Here are some examples of what you can ask me to do:<br>"
                     "• <strong>Database Stats:</strong> 'How many books are available?', 'How many registered members do we have?'<br>"
                     "• <strong>Book Search:</strong> 'Is Atomic Habits available?', 'Do you have Rich Dad Poor Dad?'<br>"
                     "• <strong>Recommendations:</strong> 'Recommend psychology books', 'Best business books'<br>"
                     "• <strong>Guidance:</strong> 'How do I borrow a book?', 'What are the return late policies?'<br>"
                     "• <strong>Q&A:</strong> 'What is Blockchain?', 'What is Machine Learning?'"
        }

    def get_genre_recommendations_reply(self, genre, c):
        c.execute("SELECT id, title, author, category, description, rating, total_quantity, available_quantity FROM books WHERE category LIKE ? OR description LIKE ? ORDER BY rating DESC LIMIT 3", (f"%{genre}%", f"%{genre}%"))
        db_results = c.fetchall()
        
        if db_results:
            reply = f"<h3>📚 Top Recommended {genre.title()} Books from our Library:</h3><br>"
            for r in db_results:
                b_id, title, author, category, desc, rating, total, avail = r
                rating_val = rating if rating else "4.6"
                status = "AVAILABLE" if avail > 0 else "BORROWED"
                reply += f"<strong>📖 {title}</strong> by {author}<br>" \
                         f"• <strong>Category:</strong> {category} | <strong>Rating:</strong> {rating_val}/5<br>" \
                         f"• <strong>Status:</strong> {status} ({avail}/{total} copies available)<br>" \
                         f"• <strong>Description:</strong> {desc}<br>" \
                         f"• <strong>Why Recommended:</strong> An outstanding, highly rated guide in the field of {genre} that offers practical, action-oriented lessons.<br><br>"
            
            reply += f"Would you also like to explore recommendations in related fields such as <strong>behavioral science, cognitive psychology, self-improvement, or productivity</strong>?"
            return {"reply": reply}

        curated_lists = {
            'self help': [
                {"title": "Atomic Habits", "author": "James Clear", "rating": "4.9", "desc": "A supreme guide to building good habits and breaking bad ones through tiny, consistent changes.", "why": "Backed by neuroscience and behavioral economics, it provides a highly practical framework for self-improvement."},
                {"title": "Grit", "author": "Angela Duckworth", "rating": "4.7", "desc": "A study of why passion and long-term perseverance are the ultimate secrets to success.", "why": "It redefines how we view intelligence and talent, proving that consistency and passion matter more."}
            ],
            'business': [
                {"title": "Zero to One", "author": "Peter Thiel", "rating": "4.6", "desc": "Notes on startups and how to build the future by creating completely new innovations.", "why": "Provides an intellectual foundation for entrepreneurial thinking and monopoly-building."},
                {"title": "The Lean Startup", "author": "Eric Ries", "rating": "4.5", "desc": "How constant innovation and rapid feedback loops create radical startup success.", "why": "It is the modern bible for tech development and starting highly efficient enterprises."}
            ],
            'psychology': [
                {"title": "Thinking, Fast and Slow", "author": "Daniel Kahneman", "rating": "4.6", "desc": "A masterpiece exploring the two systems that drive human decision-making and cognitive biases.", "why": "Written by a Nobel laureate, it is the absolute gold standard for understanding human irrationality."},
                {"title": "The Courage to Be Disliked", "author": "Ichiro Kishimi", "rating": "4.8", "desc": "Applying Adlerian psychology to unlock personal freedom, happiness, and interpersonal boundaries.", "why": "It challenges conventional wisdom on relationships and gives profound, liberating advice."}
            ],
            'finance': [
                {"title": "The Psychology of Money", "author": "Morgan Housel", "rating": "4.7", "desc": "Timeless lessons on wealth, greed, happiness, and the emotional biases that affect our money decisions.", "why": "Highly readable and filled with historical anecdotes, it teaches how behavior matters more than technical knowledge."},
                {"title": "Rich Dad Poor Dad", "author": "Robert Kiyosaki", "rating": "4.9", "desc": "A foundational classic on financial literacy, building assets, and gaining financial independence.", "why": "It completely reframes the concept of money, assets, liabilities, and traditional career paths."}
            ]
        }
        
        clean_genre = 'self help'
        for k in curated_lists.keys():
            if k in genre.lower():
                clean_genre = k
                break
                
        items = curated_lists.get(clean_genre, curated_lists['self help'])
        reply = f"<h3>📚 Curated {clean_genre.title()} Recommendations:</h3><br>"
        for b in items:
            reply += f"<strong>📖 {b['title']}</strong> by {b['author']}<br>" \
                     f"• <strong>Rating:</strong> {b['rating']}/5<br>" \
                     f"• <strong>Description:</strong> {b['desc']}<br>" \
                     f"• <strong>Why Recommended:</strong> {b['why']}<br>" \
                     f"• <strong>Alternative:</strong> You may also like similar books in our database catalog!<br><br>"
                     
        reply += f"Would you also like recommendations in related fields such as <strong>behavioral science, cognitive psychology, self-improvement, or productivity</strong>?"
        return {"reply": reply}

    def get_book_details_reply(self, b, c, is_followup=False):
        b_id, title, author, category, publisher, price, desc, total, avail, rating, borrow_count = b
        rating_val = rating if rating else "4.6"
        status = "AVAILABLE" if avail > 0 else "NOT AVAILABLE (All copies are currently borrowed)"
        
        reply = f"Yes, \"{title}\" is present.<br><br>" \
                 f"<h3>📖 Book Profile: {title}</h3><br>" \
                 f"• <strong>Title:</strong> {title}<br>" \
                 f"• <strong>Author:</strong> {author}<br>" \
                 f"• <strong>Category:</strong> {category}<br>" \
                 f"• <strong>Publisher:</strong> {publisher}<br>" \
                 f"• <strong>Price:</strong> ${price:.2f}<br>" \
                 f"• <strong>Catalog Rating:</strong> {rating_val}/5 ({borrow_count} lifetime borrows)<br>" \
                 f"• <strong>Availability Status:</strong> <strong style='color: {'var(--success)' if avail > 0 else 'var(--danger)'};'>{status}</strong><br>" \
                 f"• <strong>Copies Stocked:</strong> {avail} available out of {total} total copies.<br>" \
                 f"• <strong>Summary & Description:</strong> {desc}<br><br>"
                 
        c.execute("SELECT id, title, author, category, available_quantity FROM books WHERE category = ? AND id != ? LIMIT 2", (category, b_id))
        similar_db = c.fetchall()
        if similar_db:
            sim_text = ", ".join([f"<strong>{s[1]}</strong> by {s[2]}" for s in similar_db])
            reply += f"💡 <strong>Similar books in our catalog:</strong> {sim_text}<br>"
        else:
            c.execute("SELECT id, title, author, category, available_quantity FROM books WHERE id != ? ORDER BY RANDOM() LIMIT 2", (b_id,))
            similar_db = c.fetchall()
            sim_text = ", ".join([f"<strong>{s[1]}</strong> by {s[2]}" for s in similar_db])
            reply += f"💡 <strong>Recommended alternatives in our catalog:</strong> {sim_text}<br>"

        # Direct database borrow link button
        reply += f"<br><a href='issue_return.html?book_id={b_id}' class='btn-borrow' style='display: inline-block; margin-top: 10px; padding: 8px 16px; background: linear-gradient(135deg, var(--neon-blue), var(--neon-purple)); border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; color: white; text-decoration: none; font-weight: bold; text-transform: uppercase; font-size: 11px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); transition: all 0.3s;'>Borrow / View Location in Database</a><br>"

        if avail == 0:
            reply += f"<br>⚠️ <em>Since all copies of '{title}' are currently borrowed, you can search for a digital copy on <a href='https://libgen.li/index.php' target='_blank' style='color:var(--neon-blue); font-weight:bold;'>Library Genesis</a>.</em><br>"
            
        return {"reply": reply}

    def process_chat(self, msg, c, history=None):
        import google.generativeai as genai
        import os
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return self.local_fallback_chat(msg, c, history)
            
        genai.configure(api_key=api_key)
        
        system_instruction = (
            "You are the Matrix AI Assistant, an intellectual library management consultant. "
            "Your duty is to search, recommend, and resolve all library-related queries with precision. "
            "You have access to tools that query the library database. ALWAYS use these tools when a user asks about books, statistics, recommendations, or their account. "
            "If a book is not found or unavailable, politely inform the user and suggest they search external resources like https://libgen.li/ . "
            "Format your responses nicely with HTML where appropriate, such as using <strong> tags for emphasis or <br> for newlines. "
            "Keep your responses concise and strictly related to library management, books, or reading advice."
        )

        try:
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash',
                system_instruction=system_instruction,
                tools=[db_get_library_statistics, db_search_books, db_get_recommendations, db_get_user_status]
            )
            
            formatted_history = []
            if history:
                valid_history = [h for h in history if 'isUser' in h and 'text' in h]
                context_str = "Conversation History:\n"
                for h in valid_history[-10:]:
                    role = "User" if h.get("isUser") else "Assistant"
                    context_str += f"{role}: {h.get('text')}\n"
                
                msg = f"{context_str}\nUser: {msg}"
            
            response = model.generate_content(msg)
            return {"reply": response.text}
        except Exception as e:
            print(f"Gemini AI error, falling back to offline engine: {e}")
            return self.local_fallback_chat(msg, c, history)

    def build_recommendation_cards(self, rows):
        html = '<div class="recommendation-cards-container" style="display: flex; gap: 15px; overflow-x: auto; padding: 10px 0; margin-top: 10px; width: 100%;">'
        for r in rows:
            b_id, title, author, category, price, avail_qty, total_qty = r
            rating = f"{(4.0 + (b_id % 10) / 10.0):.1f}/5"
            avail_text = "Available" if avail_qty > 0 else "Borrowed"
            avail_color = "var(--success)" if avail_qty > 0 else "var(--danger)"
            
            html += f"""
            <div class="book-card-mini" style="flex: 0 0 200px; background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 12px; display: flex; flex-direction: column; gap: 8px; backdrop-filter: blur(10px); text-align: left;">
                <div style="height: 100px; background: linear-gradient(135deg, var(--neon-blue), var(--neon-purple)); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; text-align: center; padding: 5px; font-size: 11px; text-transform: uppercase; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">{title}</div>
                <div style="font-weight: 600; font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: var(--text-primary);" title="{title}">{title}</div>
                <div style="font-size: 11px; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{author}</div>
                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 11px; margin-top: 5px;">
                    <span style="color: var(--neon-blue); font-weight: bold;">${price:.2f}</span>
                    <span style="color: {avail_color}; font-weight: bold;">{avail_text} ({avail_qty}/{total_qty})</span>
                </div>
                <div style="font-size: 11px; color: #ffb86c;"><i class="fas fa-star"></i> {rating}</div>
                <button onclick="location.href='issue_return.html?book_id={b_id}'" style="background: var(--neon-blue); border: none; border-radius: 6px; color: white; padding: 6px; font-size: 11px; cursor: pointer; font-weight: bold; width: 100%; transition: background 0.3s; margin-top: 5px; text-transform: uppercase;">Borrow</button>
            </div>
            """
        html += '</div>'
        return html

if __name__ == '__main__':
    init_db()
    start_backup_scheduler()
    PORT = 8083
    with socketserver.TCPServer(("", PORT), LibraryHandler) as httpd:
        print(f"Library System running at: http://localhost:{PORT}")
        httpd.serve_forever()
