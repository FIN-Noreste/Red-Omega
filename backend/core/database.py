# backend/core/database.py
import sqlite3
from config import DATABASE_PATH

def init_db():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS archives (
                cid TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                uploader TEXT NOT NULL,
                file_type TEXT NOT NULL,
                tags TEXT DEFAULT '',
                network_id TEXT DEFAULT 'public',
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def save_archive(cid, filename, uploader, file_type, tags, network_id="public"):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO archives (cid, filename, uploader, file_type, tags, network_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (cid, filename, uploader, file_type, tags, network_id))
        conn.commit()

def get_all_archives():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT cid, filename, uploader, file_type, uploaded_at, tags, network_id FROM archives ORDER BY uploaded_at DESC")
        rows = cursor.fetchall()
    return [{"cid": r[0], "filename": r[1], "uploader": r[2], "type": r[3], "date": r[4], "tags": r[5], "network_id": r[6]} for r in rows]

def archive_exists(cid):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT cid FROM archives WHERE cid = ?", (cid,))
        return cursor.fetchone() is not None