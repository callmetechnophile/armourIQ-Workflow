from typing import Dict, Any
from backend.armoriq.delegation import invoke_tool

def run_extraction(raw_text: str, receipt_dict: Dict[str, Any]) -> Dict[str, Any]:
    # Extract components & classify BOM
    components = invoke_tool(
        agent_name="Extraction Agent",
        tool_name="extract_components",
        args={"raw_text": raw_text},
        receipt_dict=receipt_dict
    )
    return {
        "components": components
    }
