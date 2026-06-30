from typing import Dict, Any
from backend.armoriq.delegation import invoke_tool

def run_export(data: Dict[str, Any], receipt_dict: Dict[str, Any]) -> Dict[str, Any]:
    # Invoke formatting exporters
    pdf = invoke_tool(
        agent_name="Export Agent",
        tool_name="export_pdf",
        args={"data": data},
        receipt_dict=receipt_dict
    )
    
    csv = invoke_tool(
        agent_name="Export Agent",
        tool_name="export_csv",
        args={"data": data},
        receipt_dict=receipt_dict
    )
    
    markdown_rep = invoke_tool(
        agent_name="Export Agent",
        tool_name="export_markdown",
        args={"data": data},
        receipt_dict=receipt_dict
    )
    
    docx = invoke_tool(
        agent_name="Export Agent",
        tool_name="export_docx",
        args={"data": data},
        receipt_dict=receipt_dict
    )
    
    return {
        "pdf": pdf,
        "csv": csv,
        "markdown": markdown_rep,
        "docx": docx
    }
