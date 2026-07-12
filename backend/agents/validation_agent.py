from typing import Dict, Any, List
from backend.armoriq.delegation import invoke_tool

def run_validation(components: List[Dict[str, Any]], concept: str, receipt_dict: Dict[str, Any]) -> Dict[str, Any]:
    from backend.armoriq.delegation import delegate
    graph_validation_context = {}
    try:
        graph_receipt = delegate(
            agent_name="KnowledgeGraphAgent",
            requested_scope=["graph.read"],
            parent_receipt=receipt_dict
        )
        for comp in components:
            comp_name = comp.get("component") or comp.get("name")
            if comp_name:
                fms = invoke_tool(
                    agent_name="KnowledgeGraphAgent",
                    tool_name="graph.read",
                    args={"query_name": "find_component_failure_modes", "params": {"component_name": comp_name}},
                    receipt_dict=graph_receipt.model_dump()
                )
                conns = invoke_tool(
                    agent_name="KnowledgeGraphAgent",
                    tool_name="graph.read",
                    args={"query_name": "find_component_connections", "params": {"component_name": comp_name}},
                    receipt_dict=graph_receipt.model_dump()
                )
                graph_validation_context[comp_name] = {
                    "failure_modes": fms or [],
                    "connections": conns or []
                }
    except Exception as e:
        import logging
        logging.getLogger("ValidationAgent").warning(f"Failed to fetch validation context from Knowledge Graph: {e}")

    # Analyze engineering configurations for errors
    validation = invoke_tool(
        agent_name="Validation Agent",
        tool_name="validate_architecture",
        args={"components": components, "concept": concept},
        receipt_dict=receipt_dict
    )
    
    # Inject graph validation context into validation results
    if isinstance(validation, dict):
        validation["graph_context"] = graph_validation_context
        
    return validation
