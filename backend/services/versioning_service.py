import os
import json
from datetime import datetime
from backend.database import get_db_connection, execute_query

def save_version(project_id: str, version_num: int, data: dict, modified_by: str, change_summary: str) -> dict:
    conn = get_db_connection()
    timestamp = datetime.utcnow().isoformat()
    query = """
        INSERT INTO project_versions (project_id, version_num, data, modified_by, change_summary, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    execute_query(conn, query, (project_id, version_num, json.dumps(data), modified_by, change_summary, timestamp))
    conn.commit()
    conn.close()
    return {
        "project_id": project_id,
        "version_num": version_num,
        "change_summary": change_summary,
        "modified_by": modified_by,
        "timestamp": timestamp
    }

def get_project_versions(project_id: str) -> list:
    conn = get_db_connection()
    query = """
        SELECT version_num, modified_by, change_summary, timestamp 
        FROM project_versions 
        WHERE project_id = ? 
        ORDER BY version_num DESC
    """
    cursor = execute_query(conn, query, (project_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_version_details(project_id: str, version_num: int) -> dict:
    conn = get_db_connection()
    query = """
        SELECT version_num, data, modified_by, change_summary, timestamp 
        FROM project_versions 
        WHERE project_id = ? AND version_num = ?
    """
    cursor = execute_query(conn, query, (project_id, version_num))
    row = cursor.fetchone()
    conn.close()
    if row:
        res = dict(row)
        res["data"] = json.loads(res["data"])
        return res
    return {}

def compare_versions(project_id: str, v1_num: int, v2_num: int) -> dict:
    v1 = get_version_details(project_id, v1_num)
    v2 = get_version_details(project_id, v2_num)
    if not v1 or not v2:
        return {"error": "One or both versions not found"}
    
    d1 = v1["data"]
    d2 = v2["data"]
    
    # 1. Compare BOM components
    bom1 = {c.get("component") or c.get("name", ""): c for c in d1.get("components", [])}
    bom2 = {c.get("component") or c.get("name", ""): c for c in d2.get("components", [])}
    
    added_bom = [bom2[name] for name in bom2 if name not in bom1]
    removed_bom = [bom1[name] for name in bom1 if name not in bom2]
    updated_bom = []
    for name in bom2:
        if name in bom1:
            if bom2[name].get("cost") != bom1[name].get("cost") or bom2[name].get("selected_vendor") != bom1[name].get("selected_vendor"):
                updated_bom.append({
                    "name": name,
                    "old_cost": bom1[name].get("cost"),
                    "new_cost": bom2[name].get("cost"),
                    "old_vendor": bom1[name].get("selected_vendor"),
                    "new_vendor": bom2[name].get("selected_vendor")
                })
                
    # 2. Compare Wiring
    w1 = {f"{c.get('source')}-{c.get('target')}": c for c in d1.get("wiring_diagram", {}).get("connections", [])}
    w2 = {f"{c.get('source')}-{c.get('target')}": c for c in d2.get("wiring_diagram", {}).get("connections", [])}
    
    added_wiring = [w2[k] for k in w2 if k not in w1]
    removed_wiring = [w1[k] for k in w1 if k not in w2]
    
    # 3. Compare Code
    code_differs = d1.get("generated_code") != d2.get("generated_code")
    
    return {
        "v1": v1_num,
        "v2": v2_num,
        "bom_diff": {
            "added": added_bom,
            "removed": removed_bom,
            "updated": updated_bom
        },
        "wiring_diff": {
            "added": added_wiring,
            "removed": removed_wiring
        },
        "code_differs": code_differs
    }

def rollback_version(project_id: str, version_num: int) -> dict:
    # Fetch the version details
    v = get_version_details(project_id, version_num)
    if not v:
        raise ValueError(f"Version {version_num} of project {project_id} not found")
    
    # In version history, we don't delete history. We create a NEW version that matches the old one.
    conn = get_db_connection()
    # Get current max version
    query_max = "SELECT MAX(version_num) as max_v FROM project_versions WHERE project_id = ?"
    cursor = execute_query(conn, query_max, (project_id,))
    row = cursor.fetchone()
    current_max = row["max_v"] if row and row["max_v"] is not None else 0
    next_version = current_max + 1
    conn.close()
    
    # Save a new version with the old data but a rollback note
    save_version(
        project_id=project_id,
        version_num=next_version,
        data=v["data"],
        modified_by="Rollback Engine",
        change_summary=f"Rolled back project to v{version_num}"
    )
    
    return {
        "status": "SUCCESS",
        "version_num": next_version,
        "data": v["data"]
    }

def fork_project(project_id: str, version_num: int, new_name: str, user_id: str) -> dict:
    v = get_version_details(project_id, version_num)
    if not v:
        raise ValueError(f"Version {version_num} of project {project_id} not found")
        
    # Create the new project in project_versions as v1
    save_version(
        project_id=new_name,
        version_num=1,
        data=v["data"],
        modified_by=user_id,
        change_summary=f"Forked from {project_id} v{version_num}"
    )
    
    return {
        "status": "SUCCESS",
        "forked_project": new_name,
        "version_num": 1
    }
