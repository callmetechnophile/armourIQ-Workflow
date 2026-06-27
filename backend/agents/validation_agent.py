from typing import Dict, Any, List
from backend.armoriq.delegation import invoke_tool

def run_validation(components: List[Dict[str, Any]], concept: str, receipt_dict: Dict[str, Any]) -> Dict[str, Any]:
    # Analyze engineering configurations for errors
    validation = invoke_tool(
        agent_name="Validation Agent",
        tool_name="validate_architecture",
        args={"components": components, "concept": concept},
        receipt_dict=receipt_dict
    )
    return validation
