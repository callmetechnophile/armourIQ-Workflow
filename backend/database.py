import os
import sqlite3
import json
from datetime import datetime

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    if DATABASE_URL and (DATABASE_URL.startswith("postgres://") or DATABASE_URL.startswith("postgresql://")):
        try:
            import psycopg2
            url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
            conn = psycopg2.connect(url)
            # Set cursor factory attribute helper
            conn.cursor_factory = True
            return conn
        except Exception as e:
            print(f"[DB] PostgreSQL connection failed: {e}. Falling back to SQLite.")
            
    DB_PATH = os.path.join(os.path.dirname(__file__), "user_storage.db")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_cursor(conn):
    if hasattr(conn, "cursor_factory"):
        from psycopg2.extras import RealDictCursor
        return conn.cursor(cursor_factory=RealDictCursor)
    return conn.cursor()

def execute_query(conn, query: str, params=()):
    cursor = get_cursor(conn)
    if hasattr(conn, "cursor_factory"):
        query = query.replace("?", "%s")
    cursor.execute(query, params)
    return cursor

def init_db():
    conn = get_db_connection()
    is_postgres = hasattr(conn, "cursor_factory")
    cursor = conn.cursor()
    
    if is_postgres:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS packages (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                intent TEXT NOT NULL,
                readiness_score INTEGER NOT NULL,
                risk_score INTEGER NOT NULL,
                optimization_score INTEGER NOT NULL,
                data TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                prompt TEXT NOT NULL,
                bom TEXT NOT NULL,
                power TEXT NOT NULL,
                dependencies TEXT NOT NULL,
                wiring TEXT NOT NULL,
                papers TEXT NOT NULL,
                gantt TEXT NOT NULL,
                code TEXT NOT NULL,
                exports TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                timestamp TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id SERIAL PRIMARY KEY,
                team_id INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                email TEXT NOT NULL,
                role TEXT NOT NULL,
                joined_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                permissions TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id SERIAL PRIMARY KEY,
                project_id TEXT NOT NULL,
                section TEXT NOT NULL,
                author TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id SERIAL PRIMARY KEY,
                team_id INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_versions (
                id SERIAL PRIMARY KEY,
                project_id TEXT NOT NULL,
                version_num INTEGER NOT NULL,
                data TEXT NOT NULL,
                modified_by TEXT NOT NULL,
                change_summary TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS packages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                intent TEXT NOT NULL,
                readiness_score INTEGER NOT NULL,
                risk_score INTEGER NOT NULL,
                optimization_score INTEGER NOT NULL,
                data TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                prompt TEXT NOT NULL,
                bom TEXT NOT NULL,
                power TEXT NOT NULL,
                dependencies TEXT NOT NULL,
                wiring TEXT NOT NULL,
                papers TEXT NOT NULL,
                gantt TEXT NOT NULL,
                code TEXT NOT NULL,
                exports TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                timestamp TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                email TEXT NOT NULL,
                role TEXT NOT NULL,
                joined_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                permissions TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                section TEXT NOT NULL,
                author TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                version_num INTEGER NOT NULL,
                data TEXT NOT NULL,
                modified_by TEXT NOT NULL,
                change_summary TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        # Insert default roles into roles table
        try:
            cursor.execute("INSERT OR IGNORE INTO roles (name, permissions) VALUES ('Owner', 'full')")
            cursor.execute("INSERT OR IGNORE INTO roles (name, permissions) VALUES ('Engineer', 'technical')")
            cursor.execute("INSERT OR IGNORE INTO roles (name, permissions) VALUES ('Reviewer', 'comment')")
            cursor.execute("INSERT OR IGNORE INTO roles (name, permissions) VALUES ('Viewer', 'read')")
        except Exception:
            pass
    conn.commit()
    conn.close()

def save_package(user_id: str, intent: str, readiness: int, risk: int, optimization: int, data: dict):
    conn = get_db_connection()
    timestamp = datetime.utcnow().isoformat()
    data_str = json.dumps(data)
    
    query = """
        INSERT INTO packages (user_id, intent, readiness_score, risk_score, optimization_score, data, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    execute_query(conn, query, (user_id, intent, readiness, risk, optimization, data_str, timestamp))
    conn.commit()
    conn.close()

def get_user_history(user_id: str):
    conn = get_db_connection()
    query = """
        SELECT id, intent, readiness_score, risk_score, optimization_score, data, timestamp 
        FROM packages 
        WHERE user_id = ? 
        ORDER BY timestamp DESC
    """
    cursor = execute_query(conn, query, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            "id": row["id"],
            "intent": row["intent"],
            "readiness_score": row["readiness_score"],
            "risk_score": row["risk_score"],
            "optimization_score": row["optimization_score"],
            "data": json.loads(row["data"]),
            "timestamp": row["timestamp"]
        })
    return history
