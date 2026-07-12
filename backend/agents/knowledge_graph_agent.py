from typing import Dict, Any, List
from backend.armoriq.delegation import invoke_tool

def run_knowledge_graph_agent(intent: str, receipt_dict: Dict[str, Any]) -> Dict[str, Any]:
    # Cleans project name
    project_name = intent.replace(" ", "_")
    
    similar_projects = invoke_tool(
        agent_name="KnowledgeGraphAgent",
        tool_name="graph.read",
        args={"query_name": "find_similar_projects", "params": {"project_name": project_name}},
        receipt_dict=receipt_dict
    ) or []
    
    research = invoke_tool(
        agent_name="KnowledgeGraphAgent",
        tool_name="graph.read",
        args={"query_name": "find_related_research", "params": {"project_name": project_name}},
        receipt_dict=receipt_dict
    ) or []

    return {
        "similar_projects": similar_projects,
        "related_research": research,
        "project_name": project_name
    }

def get_alternative_components(component_name: str, receipt_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    return invoke_tool(
        agent_name="KnowledgeGraphAgent",
        tool_name="graph.read",
        args={"query_name": "find_alternative_components", "params": {"component_name": component_name}},
        receipt_dict=receipt_dict
    ) or []

def get_compatible_components(component_name: str, receipt_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    return invoke_tool(
        agent_name="KnowledgeGraphAgent",
        tool_name="graph.read",
        args={"query_name": "find_compatible_components", "params": {"component_name": component_name}},
        receipt_dict=receipt_dict
    ) or []

def get_component_datasheet(component_name: str, receipt_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    return invoke_tool(
        agent_name="KnowledgeGraphAgent",
        tool_name="graph.read",
        args={"query_name": "find_component_datasheet", "params": {"component_name": component_name}},
        receipt_dict=receipt_dict
    ) or []

def get_component_failure_modes(component_name: str, receipt_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    return invoke_tool(
        agent_name="KnowledgeGraphAgent",
        tool_name="graph.read",
        args={"query_name": "find_component_failure_modes", "params": {"component_name": component_name}},
        receipt_dict=receipt_dict
    ) or []

def get_vendor_relationships(component_name: str, receipt_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    return invoke_tool(
        agent_name="KnowledgeGraphAgent",
        tool_name="graph.read",
        args={"query_name": "find_vendor_relationships", "params": {"component_name": component_name}},
        receipt_dict=receipt_dict
    ) or []

def get_protocol_dependencies(protocol_name: str, receipt_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    return invoke_tool(
        agent_name="KnowledgeGraphAgent",
        tool_name="graph.read",
        args={"query_name": "find_protocol_dependencies", "params": {"protocol_name": protocol_name}},
        receipt_dict=receipt_dict
    ) or []

def get_power_dependencies(component_name: str, receipt_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    return invoke_tool(
        agent_name="KnowledgeGraphAgent",
        tool_name="graph.read",
        args={"query_name": "find_power_dependencies", "params": {"component_name": component_name}},
        receipt_dict=receipt_dict
    ) or []

def get_component_connections(component_name: str, receipt_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    return invoke_tool(
        agent_name="KnowledgeGraphAgent",
        tool_name="graph.read",
        args={"query_name": "find_component_connections", "params": {"component_name": component_name}},
        receipt_dict=receipt_dict
    ) or []
