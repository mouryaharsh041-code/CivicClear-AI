import sqlite3
from datetime import datetime, date, timedelta
from hashlib import md5

DB_NAME = "civicclear.db"

def get_conn():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS notices (
            notice_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            summary TEXT,
            deadline_date TEXT,
            raw_result TEXT,
            raw_hash TEXT UNIQUE,
            is_important INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def parse_deadline_date(text):
    if not text:
        return None
    import re
    text_clean = text.strip().split('\n')[0]
    try:
        for fmt in ("%Y-%m-%d", "%d %B %Y", "%d %b %Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(text_clean, fmt).date()
            except ValueError:
                continue
    except:
        pass
    return None

def save_notice(title, summary, deadline_date_str, raw_result):
    conn = get_conn()
    raw_hash = md5(raw_result.encode('utf-8')).hexdigest()
    
    existing = conn.execute("SELECT notice_id FROM notices WHERE raw_hash = ?", (raw_hash,)).fetchone()
    if existing:
        conn.close()
        return False
        
    try:
        conn.execute(
            "INSERT INTO notices (title, summary, deadline_date, raw_result, raw_hash) VALUES (?, ?, ?, ?, ?)",
            (title, summary, deadline_date_str, raw_result, raw_hash)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Save error: {e}")
        conn.close()
        return False

def get_active_notices():
    conn = get_conn()
    today = date.today()
    rows = conn.execute(
        "SELECT * FROM notices WHERE deadline_date IS NOT NULL AND deadline_date >= ? ORDER BY deadline_date ASC",
        (today.isoformat(),)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_approaching_notices(days_threshold=3):
    conn = get_conn()
    today = date.today()
    threshold = today + timedelta(days=days_threshold)
    rows = conn.execute(
        "SELECT * FROM notices WHERE deadline_date IS NOT NULL AND deadline_date > ? AND deadline_date <= ? ORDER BY deadline_date ASC",
        (today.isoformat(), threshold.isoformat())
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_expired_notices():
    conn = get_conn()
    today = date.today()
    rows = conn.execute(
        "SELECT * FROM notices WHERE deadline_date IS NOT NULL AND deadline_date < ? ORDER BY deadline_date DESC",
        (today.isoformat(),)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_important_notices():
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM notices WHERE is_important = 1 ORDER BY notice_id DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def toggle_important(notice_id, current_status):
    conn = get_conn()
    new_status = 0 if current_status == 1 else 1
    conn.execute("UPDATE notices SET is_important = ? WHERE notice_id = ?", (new_status, notice_id))
    conn.commit()
    conn.close()

def delete_notice(notice_id):
    conn = get_conn()
    conn.execute("DELETE FROM notices WHERE notice_id = ?", (notice_id,))
    conn.commit()
    conn.close()

init_db()