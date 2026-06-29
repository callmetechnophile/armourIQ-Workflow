import os
import sqlite3
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "user_storage.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
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
    conn.commit()
    conn.close()

def save_package(user_id: str, intent: str, readiness: int, risk: int, optimization: int, data: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = datetime.utcnow().isoformat()
    data_str = json.dumps(data)
    
    cursor.execute("""
        INSERT INTO packages (user_id, intent, readiness_score, risk_score, optimization_score, data, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, intent, readiness, risk, optimization, data_str, timestamp))
    
    conn.commit()
    conn.close()

def get_user_history(user_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, intent, readiness_score, risk_score, optimization_score, data, timestamp 
        FROM packages 
        WHERE user_id = ? 
        ORDER BY timestamp DESC
    """, (user_id,))
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
