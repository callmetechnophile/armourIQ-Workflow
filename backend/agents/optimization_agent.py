from typing import Dict, Any, List
from backend.armoriq.delegation import invoke_tool

def run_optimization(components: List[Dict[str, Any]], receipt_dict: Dict[str, Any]) -> Dict[str, Any]:
    from backend.armoriq.delegation import delegate
    graph_alternatives = {}
    try:
        graph_receipt = delegate(
            agent_name="KnowledgeGraphAgent",
            requested_scope=["graph.read"],
            parent_receipt=receipt_dict
        )
        for comp in components:
            comp_name = comp.get("component") or comp.get("name")
            if comp_name:
                alts = invoke_tool(
                    agent_name="KnowledgeGraphAgent",
                    tool_name="graph.read",
                    args={"query_name": "find_alternative_components", "params": {"component_name": comp_name}},
                    receipt_dict=graph_receipt.model_dump()
                )
                if alts:
                    graph_alternatives[comp_name] = alts
    except Exception as e:
        import logging
        logging.getLogger("OptimizationAgent").warning(f"Failed to fetch alternatives from Knowledge Graph: {e}")

    # Analyze cost savings and configuration optimization
    optimization = invoke_tool(
        agent_name="Optimization Agent",
        tool_name="optimize_components",
        args={"components": components},
        receipt_dict=receipt_dict
    )
    
    # Inject graph alternatives into optimization results
    if isinstance(optimization, dict):
        optimization["graph_alternatives"] = graph_alternatives
        
    return optimization
