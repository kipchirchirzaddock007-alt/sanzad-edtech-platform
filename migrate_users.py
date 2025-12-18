import sqlite3
from pathlib import Path

# DB beside this script (same folder)
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "sanzad.db"

print("Using DB:", DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("=== BEFORE: users schema (if exists) ===")
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
if cur.fetchone():
    cur.execute("PRAGMA table_info('users')")
    print(cur.fetchall())
else:
    print("No users table yet.")

print("Dropping old users table (if any)...")
cur.execute("DROP TABLE IF EXISTS users")

print("Recreating users table with new schema...")
cur.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_code TEXT UNIQUE,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    phone TEXT,
    student_id TEXT,
    institution_name TEXT,
    teacher_reg_no TEXT,
    student_reg_no TEXT,
    parent_child_name TEXT,
    parent_child_reg_no TEXT,
    status TEXT DEFAULT 'active'
)
""")

conn.commit()

print("=== AFTER: users schema ===")
cur.execute("PRAGMA table_info('users')")
print(cur.fetchall())

conn.close()
print("Migration done. You can now rerun Streamlit.")
