from fastapi import APIRouter, HTTPException, Query
from backend.graph.graph_service import GraphService
from backend.graph.synthetic_graph import build_synthetic_graph
from backend.graph.graph_visualizer import format_for_react_flow
from backend.armoriq.delegation import capture_plan, delegate, invoke_tool

router = APIRouter(prefix="/api/graph/explorer", tags=["GraphExplorer"])

@router.get("/project/{project_id}")
def get_project_ekg(project_id: str):
    try:
        # Wrap read in ArmorIQ receipt enforcer
        root_receipt = capture_plan(f"Query EKG for project {project_id}")
        graph_receipt = delegate(
            agent_name="KnowledgeGraphAgent",
            requested_scope=["graph.read"],
            parent_receipt=root_receipt.model_dump()
        )
        invoke_tool(
            agent_name="KnowledgeGraphAgent",
            tool_name="graph.read",
            args={"query_name": "find_project_graph", "params": {"project_name": project_id}},
            receipt_dict=graph_receipt.model_dump()
        )
        
        # Try AuraDB first
        service = GraphService()
        result = service.get_project_graph(project_id)

        # If AuraDB returned nothing (MockDriver fallback), use synthetic graph
        if not result.get("nodes"):
            raw = build_synthetic_graph(project_id)
            result = format_for_react_flow(raw)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch project EKG: {str(e)}")

@router.get("/component/{component_id}")
def get_component_ekg(component_id: str):
    try:
        root_receipt = capture_plan(f"Query EKG for component {component_id}")
        graph_receipt = delegate(
            agent_name="KnowledgeGraphAgent",
            requested_scope=["graph.read"],
            parent_receipt=root_receipt.model_dump()
        )
        invoke_tool(
            agent_name="KnowledgeGraphAgent",
            tool_name="graph.read",
            args={"query_name": "find_component_graph", "params": {"component_name": component_id}},
            receipt_dict=graph_receipt.model_dump()
        )
        
        service = GraphService()
        return service.get_component_graph(component_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch component EKG: {str(e)}")

@router.get("/team/{team_id}")
def get_team_ekg(team_id: str):
    try:
        root_receipt = capture_plan(f"Query EKG for team {team_id}")
        graph_receipt = delegate(
            agent_name="KnowledgeGraphAgent",
            requested_scope=["graph.read"],
            parent_receipt=root_receipt.model_dump()
        )
        invoke_tool(
            agent_name="KnowledgeGraphAgent",
            tool_name="graph.read",
            args={"query_name": "find_team_graph", "params": {"team_name": team_id}},
            receipt_dict=graph_receipt.model_dump()
        )
        
        service = GraphService()
        return service.get_team_graph(team_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch team EKG: {str(e)}")

@router.get("/user/{user_id}")
def get_user_ekg(user_id: str):
    try:
        root_receipt = capture_plan(f"Query EKG for user {user_id}")
        graph_receipt = delegate(
            agent_name="KnowledgeGraphAgent",
            requested_scope=["graph.read"],
            parent_receipt=root_receipt.model_dump()
        )
        invoke_tool(
            agent_name="KnowledgeGraphAgent",
            tool_name="graph.read",
            args={"query_name": "find_user_graph", "params": {"user_email": user_id}},
            receipt_dict=graph_receipt.model_dump()
        )
        
        service = GraphService()
        return service.get_user_graph(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user EKG: {str(e)}")

@router.get("/search")
def search_ekg(q: str = Query(..., min_length=1)):
    try:
        root_receipt = capture_plan(f"Search EKG for query {q}")
        graph_receipt = delegate(
            agent_name="KnowledgeGraphAgent",
            requested_scope=["graph.read"],
            parent_receipt=root_receipt.model_dump()
        )
        invoke_tool(
            agent_name="KnowledgeGraphAgent",
            tool_name="graph.read",
            args={"query_name": "search_graph", "params": {"query_str": q}},
            receipt_dict=graph_receipt.model_dump()
        )
        
        service = GraphService()
        return service.search_graph(q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search EKG: {str(e)}")
