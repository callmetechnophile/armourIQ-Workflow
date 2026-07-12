from fastapi import APIRouter, HTTPException
from backend.database.graph.graph_service import GraphService

router = APIRouter(prefix="/api/graph", tags=["Graph"])

@router.get("/project/{project_name}")
def get_project_graph(project_name: str):
    try:
        service = GraphService()
        graph_data = service.run_read_query("find_project_graph", {"project_name": project_name})
        if not graph_data:
            return {"nodes": [], "edges": [], "metadata": {"project": project_name}}
            
        return {
            "nodes": graph_data.get("nodes", []),
            "edges": graph_data.get("edges", []),
            "metadata": {
                "project": project_name,
                "node_count": len(graph_data.get("nodes", [])),
                "edge_count": len(graph_data.get("edges", []))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load project graph: {str(e)}")
