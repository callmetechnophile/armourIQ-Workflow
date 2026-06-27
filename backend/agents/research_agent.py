from typing import Dict, Any
from backend.armoriq.delegation import invoke_tool

def run_research(query: str, receipt_dict: Dict[str, Any]) -> Dict[str, Any]:
    # Search academic databases
    papers = invoke_tool(
        agent_name="Research Agent",
        tool_name="search_papers",
        args={"query": query},
        receipt_dict=receipt_dict
    )
    
    # Summarize top paper
    summary_details = None
    if papers:
        primary_paper_id = papers[0].get("id", "")
        summary_details = invoke_tool(
            agent_name="Research Agent",
            tool_name="summarize_papers",
            args={"paper_id": primary_paper_id},
            receipt_dict=receipt_dict
        )
        
    return {
        "papers": papers,
        "summary_details": summary_details
    }
