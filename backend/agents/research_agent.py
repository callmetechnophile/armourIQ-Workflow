from typing import Dict, Any
from backend.armoriq.delegation import invoke_tool

def run_research(query: str, receipt_dict: Dict[str, Any]) -> Dict[str, Any]:
    # Query KnowledgeGraphAgent for existing citation and contradiction network
    from backend.armoriq.delegation import delegate
    graph_research = []
    try:
        graph_receipt = delegate(
            agent_name="KnowledgeGraphAgent",
            requested_scope=["graph.read"],
            parent_receipt=receipt_dict
        )
        graph_research = invoke_tool(
            agent_name="KnowledgeGraphAgent",
            tool_name="graph.read",
            args={"query_name": "find_related_research", "params": {"project_name": query.replace(" ", "_")}},
            receipt_dict=graph_receipt.model_dump()
        )
    except Exception as e:
        import logging
        logging.getLogger("ResearchAgent").warning(f"Failed to fetch related research from Knowledge Graph: {e}")

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
        "summary_details": summary_details,
        "graph_research": graph_research
    }
