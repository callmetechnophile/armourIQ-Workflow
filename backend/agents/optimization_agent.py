from typing import Dict, Any, List
from backend.armoriq.delegation import invoke_tool

def run_optimization(components: List[Dict[str, Any]], receipt_dict: Dict[str, Any]) -> Dict[str, Any]:
    # Analyze cost savings and configuration optimization
    optimization = invoke_tool(
        agent_name="Optimization Agent",
        tool_name="optimize_components",
        args={"components": components},
        receipt_dict=receipt_dict
    )
    return optimization
