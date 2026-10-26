import sqlite3
from datetime import date, datetime

DB_FILE = "notices.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notices (
            notice_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            summary TEXT,
            deadline_date TEXT,
            raw_result TEXT,
            is_important INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on import
init_db()

def parse_deadline_date(date_str):
    if not date_str:
        return None
    try:
        for fmt in ("%Y-%m-%d", "%d %B %Y", "%d %b %Y", "%B %d, %Y"):
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue
        return None
    except Exception:
        return None

def save_notice(title, summary, deadline_date_str, raw_result):
    conn = get_connection()
    cursor = conn.cursor()
    
    status = "active"
    if deadline_date_str:
        try:
            d_date = date.fromisoformat(deadline_date_str)
            today = date.today()
            delta = (d_date - today).days
            if delta < 0:
                status = "expired"
            elif delta <= 3:
                status = "approaching"
            else:
                status = "active"
        except Exception:
            status = "active"

    # Prevent duplicates based on summary
    cursor.execute("SELECT notice_id FROM notices WHERE summary = ?", (summary,))
    if cursor.fetchone():
        conn.close()
        return False

    cursor.execute('''
        INSERT INTO notices (title, summary, deadline_date, raw_result, status, is_important)
        VALUES (?, ?, ?, ?, ?, 0)
    ''', (title, summary, deadline_date_str, raw_result, status))
    conn.commit()
    conn.close()
    return True

def toggle_important(notice_id, current_status):
    new_val = 0 if current_status == 1 else 1
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE notices SET is_important = ? WHERE notice_id = ?", (new_val, notice_id))
    conn.commit()
    conn.close()

def delete_notice(notice_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notices WHERE notice_id = ?", (notice_id,))
    conn.commit()
    conn.close()

def get_active_notices():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notices WHERE status = 'active' ORDER BY notice_id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_approaching_notices(days_threshold=3):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notices WHERE status = 'approaching' ORDER BY notice_id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_expired_notices():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notices WHERE status = 'expired' ORDER BY notice_id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_important_notices():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notices WHERE is_important = 1 ORDER BY notice_id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows
