import os
from datetime import datetime
from backend.database import get_db_connection, execute_query

def create_team(name: str) -> dict:
    import uuid
    team_uuid = str(uuid.uuid4())
    conn = get_db_connection()
    timestamp = datetime.utcnow().isoformat()
    query = "INSERT INTO teams (uuid, name, created_at) VALUES (?, ?, ?)"
    cursor = execute_query(conn, query, (team_uuid, name, timestamp))
    team_id = cursor.lastrowid
    if team_id is None:
        try:
            cursor.execute("SELECT currval(pg_get_serial_sequence('teams', 'id'))")
            team_id = cursor.fetchone()[0]
        except Exception:
            team_id = 1
    conn.commit()
    conn.close()
    
    log_activity(team_id, "system", "CREATE_TEAM", f"Team '{name}' was created.")
    
    return {"id": team_id, "uuid": team_uuid, "name": name, "created_at": timestamp}

def invite_member(team_id: int, user_id: str, email: str, role: str) -> dict:
    conn = get_db_connection()
    timestamp = datetime.utcnow().isoformat()
    query = "INSERT INTO members (team_id, user_id, email, role, joined_at) VALUES (?, ?, ?, ?, ?)"
    cursor = execute_query(conn, query, (team_id, user_id, email, role, timestamp))
    member_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    log_activity(team_id, user_id, "INVITE_MEMBER", f"User {email} was invited as {role}.")
    
    return {"id": member_id, "team_id": team_id, "user_id": user_id, "email": email, "role": role, "joined_at": timestamp}

def assign_role(member_id: int, role: str) -> bool:
    conn = get_db_connection()
    query_find = "SELECT team_id, email, user_id FROM members WHERE id = ?"
    cursor = execute_query(conn, query_find, (member_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    team_id = row["team_id"]
    email = row["email"]
    user_id = row["user_id"]
    
    query = "UPDATE members SET role = ? WHERE id = ?"
    execute_query(conn, query, (role, member_id))
    conn.commit()
    conn.close()
    
    log_activity(team_id, user_id, "ASSIGN_ROLE", f"Role of {email} was changed to {role}.")
    return True

def add_comment(project_id: str, section: str, author: str, content: str) -> dict:
    conn = get_db_connection()
    timestamp = datetime.utcnow().isoformat()
    query = "INSERT INTO comments (project_id, section, author, content, timestamp) VALUES (?, ?, ?, ?, ?)"
    cursor = execute_query(conn, query, (project_id, section, author, content, timestamp))
    comment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    log_activity(1, author, "ADD_COMMENT", f"Added comment on section '{section}': '{content[:30]}'")
    
    return {"id": comment_id, "project_id": project_id, "section": section, "author": author, "content": content, "timestamp": timestamp}

def fetch_activity_logs(team_id: int) -> list:
    conn = get_db_connection()
    query = "SELECT id, team_id, user_id, action, details, timestamp FROM activity_logs WHERE team_id = ? ORDER BY timestamp DESC"
    cursor = execute_query(conn, query, (team_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def log_activity(team_id: int, user_id: str, action: str, details: str):
    conn = get_db_connection()
    timestamp = datetime.utcnow().isoformat()
    query = "INSERT INTO activity_logs (team_id, user_id, action, details, timestamp) VALUES (?, ?, ?, ?, ?)"
    execute_query(conn, query, (team_id, user_id, action, details, timestamp))
    conn.commit()
    conn.close()

def get_team_members(team_id: int) -> list:
    conn = get_db_connection()
    query = "SELECT id, team_id, user_id, email, role, joined_at FROM members WHERE team_id = ?"
    cursor = execute_query(conn, query, (team_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_project_comments(project_id: str) -> list:
    conn = get_db_connection()
    query = "SELECT id, project_id, section, author, content, timestamp FROM comments WHERE project_id = ? ORDER BY timestamp ASC"
    cursor = execute_query(conn, query, (project_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
