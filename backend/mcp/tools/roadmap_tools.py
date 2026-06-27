import datetime
from typing import List, Dict, Any

def generate_roadmap(validation_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Produce structured milestones
    return [
        {
            "phase": 1,
            "title": "Benchtop Electrical Verification",
            "description": "Establish basic power distribution. Connect the battery pack, charge controller, and brushless ESC to check voltage stability and idle current draws.",
            "duration_days": 5,
            "deliverable": "Verified wiring schematic and functional electrical bench test."
        },
        {
            "phase": 2,
            "title": "Mechanical Fabrication & Airflow Optimization",
            "description": "3D print the custom housing. Assembly of filter components and sealing rings. Inspect and minimize pressure drops inside the cyclonic chamber.",
            "duration_days": 7,
            "deliverable": "Completed mechanical assembly housing, sealed and tested for leaks."
        },
        {
            "phase": 3,
            "title": "Control Logic & Autopilot Integration",
            "description": "Flash firmware to the controller (ESP32/Pixhawk). Set up manual throttle triggers, fail-safes, and battery telemetry readings.",
            "duration_days": 6,
            "deliverable": "Flash completion with telemetry feedback showing battery health and motor speed control."
        },
        {
            "phase": 4,
            "title": "Operational Testing & Calibration",
            "description": "Conduct field tests (run-time efficiency, battery temperature logs, suction capabilities on different debris or autonomous pathing flight test).",
            "duration_days": 4,
            "deliverable": "Final validation report documenting runtime, thermal efficiency, and overall performance."
        }
    ]

def generate_gantt(roadmap: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Convert roadmap phases into calendar dates starting from today
    start_date = datetime.date.today()
    gantt_tasks = []
    
    current_date = start_date
    for i, phase in enumerate(roadmap):
        duration = phase.get("duration_days", 5)
        end_date = current_date + datetime.timedelta(days=duration)
        
        task_id = f"task_{phase['phase']}"
        dependencies = ""
        if phase['phase'] > 1:
            dependencies = f"task_{phase['phase'] - 1}"
            
        gantt_tasks.append({
            "id": task_id,
            "name": phase["title"],
            "start": current_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
            "progress": 0 if i > 0 else 30, # Mock progress
            "dependencies": dependencies,
            "deliverable": phase["deliverable"]
        })
        # Next phase starts on the day the current phase ends
        current_date = end_date
        
    return gantt_tasks
