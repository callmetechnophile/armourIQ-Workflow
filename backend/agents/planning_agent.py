from typing import Dict, Any
from backend.armoriq.delegation import invoke_tool

def run_planning(validation_results: Dict[str, Any], receipt_dict: Dict[str, Any]) -> Dict[str, Any]:
    # Generate structured roadmap
    roadmap = invoke_tool(
        agent_name="Planning Agent",
        tool_name="generate_roadmap",
        args={"validation_results": validation_results},
        receipt_dict=receipt_dict
    )
    
    # Format roadmap into calendar-based Gantt chart data
    gantt = invoke_tool(
        agent_name="Planning Agent",
        tool_name="generate_gantt",
        args={"roadmap": roadmap},
        receipt_dict=receipt_dict
    )
    
    return {
        "roadmap": roadmap,
        "gantt": gantt
    }
