from typing import Dict, Any
from backend.armoriq.delegation import invoke_tool

def run_retrieval(query: str, receipt_dict: Dict[str, Any]) -> Dict[str, Any]:
    # Search for matching engineering designs
    projects = invoke_tool(
        agent_name="Retrieval Agent",
        tool_name="search_projects",
        args={"query": query},
        receipt_dict=receipt_dict
    )
    
    # Fetch details from the primary project source if found
    source_details = None
    if projects:
        primary_url = projects[0].get("url", "")
        source_details = invoke_tool(
            agent_name="Retrieval Agent",
            tool_name="fetch_sources",
            args={"url": primary_url},
            receipt_dict=receipt_dict
        )
        
    return {
        "projects": projects,
        "source_details": source_details
    }
