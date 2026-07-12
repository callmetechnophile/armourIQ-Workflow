import os
import json
import uuid
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from backend.database import get_db_connection, execute_query
from backend.armoriq.receipts import generate_receipt, save_tool_receipt
from backend.armoriq.delegation import log_audit_trail

def get_category_by_task_name(task_name: str) -> str:
    name_lower = task_name.lower()
    if any(k in name_lower for k in ["research", "paper", "literature", "study", "survey"]):
        return "Research"
    elif any(k in name_lower for k in ["buy", "procure", "order", "bom", "vendor", "purchase", "parts"]):
        return "Procurement"
    elif any(k in name_lower for k in ["mech", "chassis", "housing", "cad", "structure", "physical", "body"]):
        return "Mechanical"
    elif any(k in name_lower for k in ["pcb", "circuit", "solder", "elec", "schematic", "wiring", "sensor", "hardware"]):
        return "Electronics"
    elif any(k in name_lower for k in ["code", "program", "firmware", "software", "api", "backend", "frontend", "develop"]):
        return "Programming"
    elif any(k in name_lower for k in ["test", "verify", "measure", "debug", "validate", "simul"]):
        return "Testing"
    else:
        return "Deployment"

def get_color_by_category(category: str) -> str:
    # Colors: Research = Blue, Procurement = Orange, Mechanical = Gray, Electronics = Yellow, Programming = Purple, Testing = Green, Deployment = Red
    colors = {
        "Research": "Blue",
        "Procurement": "Orange",
        "Mechanical": "Gray",
        "Electronics": "Yellow",
        "Programming": "Purple",
        "Testing": "Green",
        "Deployment": "Red"
    }
    return colors.get(category, "Blue")

def generate_calendar_events(project_id: int, reminders: List[str] = None, timezone: str = "UTC") -> List[Dict[str, Any]]:
    """
    Converts project Gantt chart tasks into structured calendar event models.
    """
    conn = get_db_connection()
    query = "SELECT name, prompt, bom, papers, gantt FROM projects WHERE id = ?"
    cursor = execute_query(conn, query, (project_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise ValueError(f"Project with ID {project_id} not found.")

    project_name = row["name"]
    
    try:
        gantt_tasks = json.loads(row["gantt"]) if row["gantt"] else []
    except Exception:
        gantt_tasks = []

    events = []
    for idx, task in enumerate(gantt_tasks):
        task_name = task.get("name", f"Task {idx}")
        start_str = task.get("start", datetime.utcnow().strftime("%Y-%m-%d"))
        end_str = task.get("end", (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d"))
        deliverable = task.get("deliverable", "")
        dependencies_str = task.get("dependencies", "")
        
        # Calculate Estimated Duration
        try:
            start_dt = datetime.strptime(start_str.split("T")[0], "%Y-%m-%d")
            end_dt = datetime.strptime(end_str.split("T")[0], "%Y-%m-%d")
            duration_days = (end_dt - start_dt).days
            if duration_days <= 0:
                duration_days = 1
        except Exception:
            duration_days = 1

        category = get_category_by_task_name(task_name)
        color = get_color_by_category(category)

        # Build Description Body
        description_lines = [
            f"Project: {project_name}",
            f"Task Description: {task_name}",
            f"Estimated Duration: {duration_days} Days",
            f"Execution Phase: Phase {idx + 1}",
            f"Priority: High" if idx < 3 else "Priority: Medium",
            f"Expected Deliverables: {deliverable}",
            f"Location: WorkflowGuide AI",
            f"Category: {category}",
            f"Timezone: {timezone}"
        ]

        if dependencies_str:
            description_lines.append(f"Depends On: {dependencies_str}")

        # Add mock links
        description_lines.append(f"WorkflowGuide Project Link: http://localhost:3000/project/{project_id}")
        description_lines.append(f"Generated BOM Link: http://localhost:3000/project/{project_id}#bom")

        description = "\n".join(description_lines)

        events.append({
            "id": task.get("id", f"task-{idx}"),
            "title": task_name,
            "description": description,
            "start": start_str,
            "end": end_str,
            "location": "WorkflowGuide AI",
            "category": category,
            "color": color,
            "reminders": reminders or ["1 Day Before", "1 Hour Before", "15 Minutes Before"]
        })

    return events

def log_calendar_export(project_id: int, calendar_type: str, status: str) -> None:
    conn = get_db_connection()
    query = """
        INSERT INTO calendar_exports (project_id, calendar_type, export_time, export_status)
        VALUES (?, ?, ?, ?)
    """
    execute_query(conn, query, (str(project_id), calendar_type, datetime.utcnow().isoformat(), status))
    conn.commit()
    conn.close()

def export_google_calendar(project_id: int, events: List[Dict[str, Any]], credentials: dict = None) -> dict:
    """
    Simulates Google Calendar API export with OAuth2.
    """
    # Generate ArmorIQ receipt
    save_tool_receipt(
        "CalendarAgent",
        "Planner Agent",
        "calendar.export",
        ["calendar.export"],
        "SUCCESS",
        f"Exported {len(events)} events to Google Calendar for project {project_id}"
    )

    log_calendar_export(project_id, "Google", "Success")

    return {
        "status": "success",
        "message": f"Successfully exported {len(events)} events to Google Calendar.",
        "exported_count": len(events)
    }

def export_outlook_calendar(project_id: int, events: List[Dict[str, Any]], credentials: dict = None) -> dict:
    """
    Simulates Microsoft Graph Calendar API export with OAuth2.
    """
    # Generate ArmorIQ receipt
    save_tool_receipt(
        "CalendarAgent",
        "Planner Agent",
        "calendar.export",
        ["calendar.export"],
        "SUCCESS",
        f"Exported {len(events)} events to Outlook Calendar for project {project_id}"
    )

    log_calendar_export(project_id, "Outlook", "Success")

    return {
        "status": "success",
        "message": f"Successfully exported {len(events)} events to Outlook Calendar.",
        "exported_count": len(events)
    }

def generate_ics_file(project_id: int, events: List[Dict[str, Any]]) -> str:
    """
    Generates a valid, RFC5545 compliant universal .ics calendar file payload.
    """
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//WorkflowGuide AI//Engineering Scheduler//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]

    for event in events:
        # Convert date to YYYYMMDD
        start_date = event["start"].replace("-", "").split("T")[0]
        end_date = event["end"].replace("-", "").split("T")[0]
        
        # Ensure end date is not before start date
        if int(end_date) <= int(start_date):
            try:
                dt = datetime.strptime(start_date, "%Y%m%d") + timedelta(days=1)
                end_date = dt.strftime("%Y%m%d")
            except Exception:
                pass

        uid = f"{event['id']}-{project_id}@workflowguide.ai"
        summary = event["title"]
        description = event["description"].replace("\n", "\\n")
        location = event["location"]
        url = f"http://localhost:3000/project/{project_id}"

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTART;VALUE=DATE:{start_date}",
            f"DTEND;VALUE=DATE:{end_date}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{description}",
            f"LOCATION:{location}",
            f"URL:{url}",
            "STATUS:CONFIRMED",
            "TRANSP:TRANSPARENT"
        ])
        
        # Add reminders (VALARM)
        for reminder in event.get("reminders", []):
            trigger = "-P1D"
            if "Hour" in reminder:
                trigger = "-PT1H"
            elif "Minute" in reminder:
                trigger = "-PT15M"
            
            lines.extend([
                "BEGIN:VALARM",
                "ACTION:DISPLAY",
                f"DESCRIPTION:Reminder: {summary}",
                f"TRIGGER:{trigger}",
                "END:VALARM"
            ])

        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")
    
    # Generate ArmorIQ receipt
    save_tool_receipt(
        "CalendarAgent",
        "Planner Agent",
        "calendar.download",
        ["calendar.download"],
        "SUCCESS",
        f"Generated .ics file for project {project_id}"
    )

    log_calendar_export(project_id, "ICS", "Success")

    return "\n".join(lines)

def update_existing_calendar(project_id: int, calendar_type: str) -> dict:
    """
    Simulates updating existing calendar events for a project after Gantt chart regeneration.
    """
    # Generate ArmorIQ receipt
    save_tool_receipt(
        "CalendarAgent",
        "Planner Agent",
        "calendar.update",
        ["calendar.update"],
        "SUCCESS",
        f"Updated existing {calendar_type} Calendar events for project {project_id}"
    )

    log_calendar_export(project_id, calendar_type, "Success")

    return {
        "status": "success",
        "message": f"Successfully updated existing {calendar_type} calendar events."
    }
