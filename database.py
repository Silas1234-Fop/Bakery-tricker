"""
database.py – All database logic for the Bakery Tracker.
Uses Python's built-in sqlite3; no extra install needed.
"""

import sqlite3
import os
from datetime import date

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "bakery.db")


# ── Initialise ────────────────────────────────────────────────────────────────

def init_db():
    """Create the data folder and all tables if they don't exist yet."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = _connect()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT    NOT NULL UNIQUE,
            password  TEXT    NOT NULL,
            role      TEXT    NOT NULL DEFAULT 'worker',
            dept      TEXT
        );

        CREATE TABLE IF NOT EXISTS production (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            department  TEXT    NOT NULL,
            product     TEXT    NOT NULL,
            sack_number INTEGER NOT NULL,
            input_qty   REAL    NOT NULL,
            output_qty  REAL    NOT NULL,
            rec_date    TEXT    NOT NULL,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS packaging (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            department  TEXT    NOT NULL,
            product     TEXT    NOT NULL,
            total_packed REAL   NOT NULL,
            rec_date    TEXT    NOT NULL,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS giveaway (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            department  TEXT    NOT NULL,
            product     TEXT    NOT NULL,
            quantity    REAL    NOT NULL,
            reason      TEXT,
            rec_date    TEXT    NOT NULL,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        );
    """)

    # Seed default users if table is empty
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        default_users = [
            ("manager",  "manager123",  "manager", None),
            ("mandazi",  "mandazi123",  "worker",  "Mandazi"),
            ("bread",    "bread123",    "worker",  "Bread"),
            ("cakes",    "cakes123",    "worker",  "Cakes"),
            ("bagne",    "bagne123",    "worker",  "Bagne"),
        ]
        cur.executemany(
            "INSERT INTO users (username,password,role,dept) VALUES (?,?,?,?)",
            default_users
        )

    conn.commit()
    conn.close()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _connect():
    return sqlite3.connect(DB_PATH)


def today():
    return date.today().isoformat()


# ── Users ─────────────────────────────────────────────────────────────────────

def authenticate(username: str, password: str):
    """Return the user row dict or None."""
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT id,username,role,dept FROM users WHERE username=? AND password=?",
        (username, password)
    )
    row = cur.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "username": row[1], "role": row[2], "dept": row[3]}
    return None


# ── Production ────────────────────────────────────────────────────────────────

def add_production(department, product, sack_number, input_qty, output_qty, rec_date=None):
    conn = _connect()
    conn.execute(
        "INSERT INTO production (department,product,sack_number,input_qty,output_qty,rec_date) "
        "VALUES (?,?,?,?,?,?)",
        (department, product, sack_number, float(input_qty), float(output_qty),
         rec_date or today())
    )
    conn.commit()
    conn.close()


def get_production(department=None, rec_date=None):
    conn = _connect()
    sql = "SELECT * FROM production WHERE 1=1"
    params = []
    if department:
        sql += " AND department=?"; params.append(department)
    if rec_date:
        sql += " AND rec_date=?";   params.append(rec_date)
    sql += " ORDER BY created_at DESC"
    cur = conn.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    cols = ["id","department","product","sack_number","input_qty","output_qty","rec_date","created_at"]
    return [dict(zip(cols, r)) for r in rows]


def delete_production(record_id):
    conn = _connect()
    conn.execute("DELETE FROM production WHERE id=?", (record_id,))
    conn.commit()
    conn.close()


# ── Packaging ─────────────────────────────────────────────────────────────────

def add_packaging(department, product, total_packed, rec_date=None):
    conn = _connect()
    conn.execute(
        "INSERT INTO packaging (department,product,total_packed,rec_date) VALUES (?,?,?,?)",
        (department, product, float(total_packed), rec_date or today())
    )
    conn.commit()
    conn.close()


def get_packaging(department=None, rec_date=None):
    conn = _connect()
    sql = "SELECT * FROM packaging WHERE 1=1"
    params = []
    if department:
        sql += " AND department=?"; params.append(department)
    if rec_date:
        sql += " AND rec_date=?";   params.append(rec_date)
    sql += " ORDER BY created_at DESC"
    cur = conn.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    cols = ["id","department","product","total_packed","rec_date","created_at"]
    return [dict(zip(cols, r)) for r in rows]


def delete_packaging(record_id):
    conn = _connect()
    conn.execute("DELETE FROM packaging WHERE id=?", (record_id,))
    conn.commit()
    conn.close()


# ── Giveaway ──────────────────────────────────────────────────────────────────

def add_giveaway(department, product, quantity, reason="", rec_date=None):
    conn = _connect()
    conn.execute(
        "INSERT INTO giveaway (department,product,quantity,reason,rec_date) VALUES (?,?,?,?,?)",
        (department, product, float(quantity), reason, rec_date or today())
    )
    conn.commit()
    conn.close()


def get_giveaway(department=None, rec_date=None):
    conn = _connect()
    sql = "SELECT * FROM giveaway WHERE 1=1"
    params = []
    if department:
        sql += " AND department=?"; params.append(department)
    if rec_date:
        sql += " AND rec_date=?";   params.append(rec_date)
    sql += " ORDER BY created_at DESC"
    cur = conn.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    cols = ["id","department","product","quantity","reason","rec_date","created_at"]
    return [dict(zip(cols, r)) for r in rows]


def delete_giveaway(record_id):
    conn = _connect()
    conn.execute("DELETE FROM giveaway WHERE id=?", (record_id,))
    conn.commit()
    conn.close()


# ── Reconciliation ────────────────────────────────────────────────────────────

def reconcile(department=None, rec_date=None):
    """
    Returns a dict with produced, packed, given, real_loss, efficiency.
    Optionally filtered by department and/or date.
    """
    conn = _connect()

    def _sum(table, col, dept, dt):
        sql = f"SELECT COALESCE(SUM({col}),0) FROM {table} WHERE 1=1"
        p = []
        if dept: sql += " AND department=?"; p.append(dept)
        if dt:   sql += " AND rec_date=?";   p.append(dt)
        return conn.execute(sql, p).fetchone()[0]

    produced = _sum("production", "output_qty",   department, rec_date)
    packed   = _sum("packaging",  "total_packed",  department, rec_date)
    given    = _sum("giveaway",   "quantity",      department, rec_date)

    real_loss  = produced - packed - given
    efficiency = round((packed / produced * 100), 1) if produced > 0 else 0.0

    conn.close()
    return {
        "produced":   produced,
        "packed":     packed,
        "given":      given,
        "real_loss":  real_loss,
        "efficiency": efficiency,
    }


def reconcile_by_dept(rec_date=None):
    """Returns reconciliation stats broken down per department."""
    depts = ["Mandazi", "Bread", "Cakes", "Bagne"]
    return {d: reconcile(department=d, rec_date=rec_date) for d in depts}
