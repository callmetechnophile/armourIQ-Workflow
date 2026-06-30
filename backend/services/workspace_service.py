import json
from datetime import datetime
from typing import List, Dict, Any
from backend.database import get_db_connection, execute_query

def save_project(user_id: str, name: str, prompt: str, bom: List[Dict[str, Any]], 
                 power: Dict[str, Any], dependencies: Dict[str, Any], 
                 wiring: Dict[str, Any], papers: List[Dict[str, Any]], 
                 gantt: List[Dict[str, Any]], code: Dict[str, Any], 
                 exports: Dict[str, Any]) -> Dict[str, Any]:
    """
    Saves a project workspace package to the database.
    Increments the version number if a project with the same name already exists for the user.
    """
    conn = get_db_connection()
    timestamp = datetime.utcnow().isoformat()
    
    # 1. Fetch current max version for the user's project
    query_ver = "SELECT MAX(version) as max_v FROM projects WHERE user_id = ? AND name = ?"
    cursor = execute_query(conn, query_ver, (user_id, name))
    row = cursor.fetchone()
    
    current_max = row["max_v"] if row and row["max_v"] is not None else 0
    next_version = current_max + 1
    
    # 2. Insert project version row
    query_ins = """
        INSERT INTO projects (user_id, name, prompt, bom, power, dependencies, wiring, papers, gantt, code, exports, version, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    execute_query(conn, query_ins, (
        user_id, name, prompt,
        json.dumps(bom), json.dumps(power), json.dumps(dependencies),
        json.dumps(wiring), json.dumps(papers), json.dumps(gantt),
        json.dumps(code), json.dumps(exports), next_version, timestamp
    ))
    
    conn.commit()
    conn.close()
    
    return {
        "status": "SUCCESS",
        "name": name,
        "version": next_version,
        "timestamp": timestamp
    }

def list_user_projects(user_id: str) -> List[Dict[str, Any]]:
    """
    Lists unique projects saved by the user showing the latest version for each.
    """
    conn = get_db_connection()
    # Group by name and get maximum version row details
    # Postgres and SQLite syntax can differ slightly on DISTINCT ON.
    # To keep it completely cross-compatible, we select all ordered by name, version DESC
    query = """
        SELECT id, name, prompt, version, timestamp 
        FROM projects 
        WHERE user_id = ? 
        ORDER BY name ASC, version DESC
    """
    cursor = execute_query(conn, query, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    projects = []
    seen_names = set()
    for row in rows:
        if row["name"] not in seen_names:
            seen_names.add(row["name"])
            projects.append({
                "id": row["id"],
                "name": row["name"],
                "prompt": row["prompt"],
                "version": row["version"],
                "timestamp": row["timestamp"]
            })
            
    return projects

def get_project_versions(user_id: str, name: str) -> List[Dict[str, Any]]:
    """
    Retrieves all version history entries for a specific project name.
    """
    conn = get_db_connection()
    query = """
        SELECT id, name, version, timestamp, prompt 
        FROM projects 
        WHERE user_id = ? AND name = ? 
        ORDER BY version DESC
    """
    cursor = execute_query(conn, query, (user_id, name))
    rows = cursor.fetchall()
    conn.close()
    
    versions = []
    for row in rows:
        versions.append({
            "id": row["id"],
            "name": row["name"],
            "version": row["version"],
            "prompt": row["prompt"],
            "timestamp": row["timestamp"]
        })
    return versions

def load_project(user_id: str, project_id: int) -> Dict[str, Any]:
    """
    Loads a specific project version from the database.
    """
    conn = get_db_connection()
    query = """
        SELECT id, name, prompt, bom, power, dependencies, wiring, papers, gantt, code, exports, version, timestamp 
        FROM projects 
        WHERE user_id = ? AND id = ?
    """
    cursor = execute_query(conn, query, (user_id, project_id))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise ValueError(f"Project version ID {project_id} not found.")
        
    return {
        "id": row["id"],
        "name": row["name"],
        "prompt": row["prompt"],
        "bom": json.loads(row["bom"]),
        "power": json.loads(row["power"]),
        "dependencies": json.loads(row["dependencies"]),
        "wiring": json.loads(row["wiring"]),
        "papers": json.loads(row["papers"]),
        "gantt": json.loads(row["gantt"]),
        "code": json.loads(row["code"]),
        "exports": json.loads(row["exports"]),
        "version": row["version"],
        "timestamp": row["timestamp"]
    }

def clone_project(user_id: str, project_id: int, new_name: str) -> Dict[str, Any]:
    """
    Duplicates an existing project version under a new name with version 1.
    """
    proj = load_project(user_id, project_id)
    return save_project(
        user_id=user_id,
        name=new_name,
        prompt=proj["prompt"],
        bom=proj["bom"],
        power=proj["power"],
        dependencies=proj["dependencies"],
        wiring=proj["wiring"],
        papers=proj["papers"],
        gantt=proj["gantt"],
        code=proj["code"],
        exports=proj["exports"]
    )

def delete_project(user_id: str, project_id: int) -> Dict[str, Any]:
    """
    Deletes a specific project entry version.
    """
    conn = get_db_connection()
    query = "DELETE FROM projects WHERE user_id = ? AND id = ?"
    execute_query(conn, query, (user_id, project_id))
    conn.commit()
    conn.close()
    return {"status": "DELETED", "id": project_id}
