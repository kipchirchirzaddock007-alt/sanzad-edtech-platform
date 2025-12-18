import sqlite3
from pathlib import Path
import hashlib

# Anchor DB file at project root (one level above src)
BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "sanzad.db"


def _get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = _get_connection()
    cur = conn.cursor()

    # Institutions
    cur.execute("""
    CREATE TABLE IF NOT EXISTS institutions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        code TEXT,
        status TEXT,           -- 'pending' or 'approved'
        country TEXT,
        city TEXT,
        details TEXT
    )
    """)

    # Emergencies
    cur.execute("""
    CREATE TABLE IF NOT EXISTS emergencies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT,
        role TEXT,
        description TEXT,
        location TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # New users (accounts) table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_code TEXT UNIQUE,         -- 10-digit platform code
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,            -- 'Student','Teacher','Parent','Institution','Super Admin'
        phone TEXT,
        student_id TEXT,
        institution_name TEXT,
        teacher_reg_no TEXT,
        student_reg_no TEXT,
        parent_child_name TEXT,
        parent_child_reg_no TEXT,
        status TEXT DEFAULT 'active'   -- 'active','blocked'
    )
    """)

    # Smart Teacher: assignments created by teachers
    cur.execute("""
    CREATE TABLE IF NOT EXISTS assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTEGER NOT NULL,          -- users.id of teacher
        title TEXT NOT NULL,
        subject TEXT,
        class_name TEXT,
        due_date TEXT,
        max_points INTEGER,
        status TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (teacher_id) REFERENCES users(id)
    )
    """)

    # Smart Teacher: student submissions
    cur.execute("""
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assignment_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        filename TEXT,
        file_bytes BLOB,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (assignment_id) REFERENCES assignments(id),
        FOREIGN KEY (student_id) REFERENCES users(id)
    )
    """)

    # Smart Teacher: grades given by teacher
    cur.execute("""
    CREATE TABLE IF NOT EXISTS grades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        submission_id INTEGER NOT NULL,
        teacher_id INTEGER NOT NULL,
        score REAL,
        max_points REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (submission_id) REFERENCES submissions(id),
        FOREIGN KEY (teacher_id) REFERENCES users(id)
    )
    """)

    # NEW: shared items table (Lost & Found + Marketplace)
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,          -- 'lost_found' or 'marketplace'
        subtype TEXT NOT NULL,       -- 'lost', 'found', 'sale', 'wanted', etc.
        title TEXT NOT NULL,
        description TEXT,
        owner_user_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'open',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (owner_user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS item_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        sender_user_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (item_id) REFERENCES items(id),
        FOREIGN KEY (sender_user_id) REFERENCES users(id)
    );
    """)

    conn.commit()
    conn.close()



# ---------- Institution helpers ----------

def add_institution_application(name, country, city, details, code=""):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR IGNORE INTO institutions (name, code, status, country, city, details)
        VALUES (?, ?, 'pending', ?, ?, ?)
        """,
        (name, code, country, city, details),
    )
    conn.commit()
    conn.close()


def approve_institution_db(name, code=None):
    conn = _get_connection()
    cur = conn.cursor()
    if code:
        cur.execute(
            "UPDATE institutions SET status='approved', code=? WHERE name=?",
            (code, name),
        )
    else:
        cur.execute(
            "UPDATE institutions SET status='approved' WHERE name=?",
            (name,),
        )
    conn.commit()
    conn.close()


def delete_institution_application(name):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM institutions WHERE name=? AND status='pending'", (name,))
    conn.commit()
    conn.close()


def list_institutions(status=None):
    conn = _get_connection()
    cur = conn.cursor()
    if status:
        cur.execute(
            "SELECT id, name, code, status, country, city, details FROM institutions WHERE status=?",
            (status,),
        )
    else:
        cur.execute(
            "SELECT id, name, code, status, country, city, details FROM institutions"
        )
    rows = cur.fetchall()
    conn.close()
    return rows


# ---------- User account helpers ----------

def _hash_password(raw_password: str) -> str:
    return hashlib.sha256(raw_password.encode("utf-8")).hexdigest()


def _generate_user_code(conn) -> str:
    """
    Generate next 10-digit user_code in registration order.
    If the column does not exist yet (old DB), add it without dropping data.
    """
    cur = conn.cursor()

    # Ensure user_code column exists on old databases
    cur.execute("PRAGMA table_info('users')")
    cols = [row[1] for row in cur.fetchall()]
    if "user_code" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN user_code TEXT")
        conn.commit()

    # Get last code and increment
    cur.execute("SELECT user_code FROM users ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    if row is None or not row[0]:
        return "0000000001"
    last_code = int(row[0])
    next_code = last_code + 1
    return f"{next_code:010d}"


def create_user(
    full_name: str,
    email: str,
    raw_password: str,
    role: str,
    phone: str = "",
    student_id: str = "",
    institution_name: str = "",
    teacher_reg_no: str = "",
    student_reg_no: str = "",
    parent_child_name: str = "",
    parent_child_reg_no: str = "",
):
    """
    Create a new user.
    Returns a dict with user details on success, or None if email/user_code violates UNIQUE.
    """
    conn = _get_connection()
    cur = conn.cursor()

    password_hash = _hash_password(raw_password)
    user_code = _generate_user_code(conn)

    try:
        cur.execute(
            """
            INSERT INTO users (
                user_code, full_name, email, password_hash, role, phone,
                student_id, institution_name, teacher_reg_no, student_reg_no,
                parent_child_name, parent_child_reg_no, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
            """,
            (
                user_code,
                full_name.strip(),
                email.strip().lower(),
                password_hash,
                role,
                phone.strip(),
                student_id.strip(),
                institution_name.strip(),
                teacher_reg_no.strip(),
                student_reg_no.strip(),
                parent_child_name.strip(),
                parent_child_reg_no.strip(),
            ),
        )
        conn.commit()
        user_id = cur.lastrowid
    except sqlite3.IntegrityError:
        # UNIQUE constraint failed (likely email or user_code)
        conn.rollback()
        conn.close()
        return None
    else:
        conn.close()
        return {
            "id": user_id,
            "user_code": user_code,
            "full_name": full_name.strip(),
            "email": email.strip().lower(),
            "role": role,
            "phone": phone.strip(),
            "student_id": student_id.strip(),
            "institution_name": institution_name.strip(),
            "teacher_reg_no": teacher_reg_no.strip(),
            "student_reg_no": student_reg_no.strip(),
            "parent_child_name": parent_child_name.strip(),
            "parent_child_reg_no": parent_child_reg_no.strip(),
            "status": "active",
        }


def get_user_by_email(email: str):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, user_code, full_name, email, password_hash, role, phone,
               student_id, institution_name, teacher_reg_no, student_reg_no,
               parent_child_name, parent_child_reg_no, status
        FROM users
        WHERE email = ?
        """,
        (email.strip().lower(),),
    )
    row = cur.fetchone()
    conn.close()
    if row is None:
        return None
    (
        id_,
        user_code,
        full_name,
        email,
        password_hash,
        role,
        phone,
        student_id,
        institution_name,
        teacher_reg_no,
        student_reg_no,
        parent_child_name,
        parent_child_reg_no,
        status,
    ) = row
    return {
        "id": id_,
        "user_code": user_code,
        "full_name": full_name,
        "email": email,
        "password_hash": password_hash,
        "role": role,
        "phone": phone,
        "student_id": student_id,
        "institution_name": institution_name,
        "teacher_reg_no": teacher_reg_no,
        "student_reg_no": student_reg_no,
        "parent_child_name": parent_child_name,
        "parent_child_reg_no": parent_child_reg_no,
        "status": status,
    }


def verify_login(email: str, raw_password: str):
    user = get_user_by_email(email)
    if user is None:
        return None
    if user["status"] != "active":
        return None
    if user["password_hash"] != _hash_password(raw_password):
        return None
    return user


def set_user_status(user_id: int, status: str):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET status = ? WHERE id = ?",
        (status, user_id),
    )
    conn.commit()
    conn.close()


def list_users():
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, user_code, full_name, email, role, phone,
               institution_name, status
        FROM users
        ORDER BY id ASC
        """
    )
    rows = cur.fetchall()
    conn.close()
    users = []
    for r in rows:
        users.append(
            {
                "id": r[0],
                "user_code": r[1],
                "full_name": r[2],
                "email": r[3],
                "role": r[4],
                "phone": r[5],
                "institution_name": r[6],
                "status": r[7],
            }
        )
    return users


# ---------- Smart Teacher helpers ----------

def create_assignment_db(
    teacher_id: int,
    title: str,
    subject: str,
    class_name: str,
    due_date: str,
    max_points: int,
    status: str,
    description: str,
):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO assignments
        (teacher_id, title, subject, class_name, due_date, max_points, status, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            teacher_id,
            title.strip(),
            subject.strip(),
            class_name.strip(),
            str(due_date),
            int(max_points),
            status.strip(),
            description.strip(),
        ),
    )
    conn.commit()
    assignment_id = cur.lastrowid
    conn.close()
    return assignment_id


def list_teacher_assignments(teacher_id: int):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, title, subject, class_name, due_date, max_points, status, description
        FROM assignments
        WHERE teacher_id = ?
        ORDER BY created_at DESC
        """,
        (teacher_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def list_student_assignments(student_user: dict):
    institution = (student_user.get("institution_name") or "").strip()
    department = (student_user.get("student_id") or "").strip()

    conn = _get_connection()
    cur = conn.cursor()

    if department:
        cur.execute(
            """
            SELECT a.id, a.title, a.subject, a.class_name, a.due_date, a.max_points, a.status, a.description
            FROM assignments a
            JOIN users u ON a.teacher_id = u.id
            WHERE u.institution_name = ?
              AND a.status = 'Published'
              AND a.class_name = ?
            ORDER BY a.created_at DESC
            """,
            (institution, department),
        )
    else:
        cur.execute(
            """
            SELECT a.id, a.title, a.subject, a.class_name, a.due_date, a.max_points, a.status, a.description
            FROM assignments a
            JOIN users u ON a.teacher_id = u.id
            WHERE u.institution_name = ?
              AND a.status = 'Published'
            ORDER BY a.created_at DESC
            """,
            (institution,),
        )

    rows = cur.fetchall()
    conn.close()
    return rows


def save_submission_db(
    assignment_id: int,
    student_id: int,
    filename: str,
    file_bytes: bytes,
):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO submissions (assignment_id, student_id, filename, file_bytes)
        VALUES (?, ?, ?, ?)
        """,
        (assignment_id, student_id, filename, file_bytes),
    )
    conn.commit()
    sub_id = cur.lastrowid
    conn.close()
    return sub_id


def list_teacher_submissions(teacher_id: int):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT s.id, s.assignment_id, s.student_id, s.filename, s.submitted_at,
               a.title, a.class_name, u.full_name
        FROM submissions s
        JOIN assignments a ON s.assignment_id = a.id
        JOIN users u ON s.student_id = u.id
        WHERE a.teacher_id = ?
        ORDER BY s.submitted_at DESC
        """,
        (teacher_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def list_student_submissions(student_id: int):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT s.id, s.assignment_id, s.filename, s.submitted_at,
               a.title, a.subject, a.class_name
        FROM submissions s
        JOIN assignments a ON s.assignment_id = a.id
        WHERE s.student_id = ?
        ORDER BY s.submitted_at DESC
        """,
        (student_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def save_grade_db(
    submission_id: int,
    teacher_id: int,
    score: float,
    max_points: float,
):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO grades (submission_id, teacher_id, score, max_points)
        VALUES (?, ?, ?, ?)
        """,
        (submission_id, teacher_id, score, max_points),
    )
    conn.commit()
    grade_id = cur.lastrowid
    conn.close()
    return grade_id


def list_student_grades(student_id: int):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT g.id, g.score, g.max_points, g.created_at,
               a.title, a.subject, a.class_name
        FROM grades g
        JOIN submissions s ON g.submission_id = s.id
        JOIN assignments a ON s.assignment_id = a.id
        WHERE s.student_id = ?
        ORDER BY g.created_at DESC
        """,
        (student_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows
