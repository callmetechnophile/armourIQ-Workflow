"""
bundle_service.py
-----------------
Saves the entire active pipeline as a single compressed JSON bundle
into the `workspace_bundles` table in PostgreSQL (or SQLite fallback).

Bundle format
-------------
{
  "schema_version": "1.0",
  "saved_at": "<ISO timestamp>",
  "user_id": "...",
  "name": "...",
  "description": "...",
  "bundle": {
    "intent":            <str>,
    "components":        [...],
    "cost_summary":      {...},
    "power_analysis":    {...},
    "dependency_graph":  {...},
    "wiring_diagram":    {...},
    "research_papers":   [...],
    "gantt":             [...],
    "roadmap":           [...],
    "voltage_risks":     [...],
    "pin_mapping":       [...],
    "contradictions":    [...],
    "thermal_analysis":  {...},
    "decision_trace":    [...],
    "audit_trail":       [...],
    "bom_exports":       {...},
    "code":              {...},
    "version_history":   {...},
    "target_days":       <int>
  }
}

The entire bundle dict is gzip-compressed + base64-encoded before storage
so one column holds everything without hitting row-size limits.
"""
import json
import gzip
import base64
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.database import get_db_connection, execute_query


# ── Schema init ───────────────────────────────────────────────────────────────

SQLITE_CREATE = """
CREATE TABLE IF NOT EXISTS workspace_bundles (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT    NOT NULL,
    name        TEXT    NOT NULL,
    description TEXT    DEFAULT '',
    bundle_blob TEXT    NOT NULL,
    checksum    TEXT    NOT NULL,
    bundle_size INTEGER NOT NULL,
    field_count INTEGER NOT NULL,
    version     INTEGER NOT NULL DEFAULT 1,
    saved_at    TEXT    NOT NULL
)
"""

POSTGRES_CREATE = """
CREATE TABLE IF NOT EXISTS workspace_bundles (
    id          SERIAL  PRIMARY KEY,
    user_id     TEXT    NOT NULL,
    name        TEXT    NOT NULL,
    description TEXT    DEFAULT '',
    bundle_blob TEXT    NOT NULL,
    checksum    TEXT    NOT NULL,
    bundle_size INTEGER NOT NULL,
    field_count INTEGER NOT NULL,
    version     INTEGER NOT NULL DEFAULT 1,
    saved_at    TEXT    NOT NULL
)
"""


def ensure_bundle_table():
    conn = get_db_connection()
    is_postgres = hasattr(conn, "cursor_factory")
    cursor = conn.cursor()
    cursor.execute(POSTGRES_CREATE if is_postgres else SQLITE_CREATE)
    conn.commit()
    conn.close()


# ── Compression helpers ───────────────────────────────────────────────────────

def _compress(data: dict) -> str:
    """Gzip-compress a dict and return a base64 string."""
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    compressed = gzip.compress(raw, compresslevel=9)
    return base64.b64encode(compressed).decode("ascii")


def _decompress(blob: str) -> dict:
    """Reverse of _compress."""
    compressed = base64.b64decode(blob.encode("ascii"))
    raw = gzip.decompress(compressed)
    return json.loads(raw.decode("utf-8"))


def _checksum(data: dict) -> str:
    raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


# ── Core save ─────────────────────────────────────────────────────────────────

def save_bundle(
    user_id: str,
    name: str,
    pipeline_data: Dict[str, Any],
    description: str = ""
) -> Dict[str, Any]:
    """
    Compresses the full pipeline_data dict and inserts it as a new versioned
    bundle row.  Returns save metadata (id, version, checksum, size).
    """
    ensure_bundle_table()

    saved_at = datetime.now(timezone.utc).isoformat()

    bundle_doc = {
        "schema_version": "1.0",
        "saved_at": saved_at,
        "user_id": user_id,
        "name": name,
        "description": description,
        "bundle": pipeline_data
    }

    blob       = _compress(bundle_doc)
    chk        = _checksum(bundle_doc)
    blob_size  = len(blob)                           # bytes of the compressed b64 string
    field_cnt  = len([k for k, v in pipeline_data.items() if v])

    conn = get_db_connection()

    # Determine next version
    cursor = execute_query(
        conn,
        "SELECT MAX(version) as max_v FROM workspace_bundles WHERE user_id = ? AND name = ?",
        (user_id, name)
    )
    row = cursor.fetchone()
    next_version = ((row["max_v"] or 0) + 1) if row else 1

    execute_query(conn,
        """
        INSERT INTO workspace_bundles
            (user_id, name, description, bundle_blob, checksum, bundle_size, field_count, version, saved_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, name, description, blob, chk, blob_size, field_cnt, next_version, saved_at)
    )
    conn.commit()

    # Fetch the new row id
    cursor2 = execute_query(
        conn,
        "SELECT id FROM workspace_bundles WHERE user_id = ? AND name = ? AND version = ?",
        (user_id, name, next_version)
    )
    new_row = cursor2.fetchone()
    new_id  = new_row["id"] if new_row else -1
    conn.close()

    return {
        "status":       "SAVED",
        "id":           new_id,
        "name":         name,
        "version":      next_version,
        "checksum":     chk,
        "bundle_size":  blob_size,
        "field_count":  field_cnt,
        "saved_at":     saved_at,
    }


# ── List / Load / Delete ──────────────────────────────────────────────────────

def list_bundles(user_id: str) -> List[Dict[str, Any]]:
    ensure_bundle_table()
    conn = get_db_connection()
    cursor = execute_query(conn,
        """
        SELECT id, name, description, checksum, bundle_size, field_count, version, saved_at
        FROM workspace_bundles
        WHERE user_id = ?
        ORDER BY name ASC, version DESC
        """,
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    results = []
    seen = set()
    for r in rows:
        key = r["name"]
        if key not in seen:
            seen.add(key)
        results.append({
            "id":          r["id"],
            "name":        r["name"],
            "description": r["description"],
            "checksum":    r["checksum"],
            "bundle_size": r["bundle_size"],
            "field_count": r["field_count"],
            "version":     r["version"],
            "saved_at":    r["saved_at"],
        })
    return results


def load_bundle(user_id: str, bundle_id: int) -> Dict[str, Any]:
    ensure_bundle_table()
    conn = get_db_connection()
    cursor = execute_query(conn,
        "SELECT * FROM workspace_bundles WHERE user_id = ? AND id = ?",
        (user_id, bundle_id)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise ValueError(f"Bundle ID {bundle_id} not found.")

    doc = _decompress(row["bundle_blob"])
    return {
        "id":           row["id"],
        "name":         row["name"],
        "description":  row["description"],
        "version":      row["version"],
        "checksum":     row["checksum"],
        "bundle_size":  row["bundle_size"],
        "field_count":  row["field_count"],
        "saved_at":     row["saved_at"],
        "pipeline":     doc.get("bundle", {}),
    }


def delete_bundle(user_id: str, bundle_id: int) -> Dict[str, Any]:
    ensure_bundle_table()
    conn = get_db_connection()
    execute_query(conn,
        "DELETE FROM workspace_bundles WHERE user_id = ? AND id = ?",
        (user_id, bundle_id)
    )
    conn.commit()
    conn.close()
    return {"status": "DELETED", "id": bundle_id}
