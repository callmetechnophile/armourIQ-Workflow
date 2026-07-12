import logging
from backend.database.graph.graph_connection import get_graph_driver
from backend.database.graph.graph_schema import init_constraints
import backend.graph.graph_queries as queries
from backend.graph.graph_loader import ingest_complete_project_graph
from backend.graph.graph_builder import build_graph_payload
from backend.graph.graph_visualizer import format_for_react_flow

logger = logging.getLogger("GraphExplorerService")

class GraphService:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GraphService, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self):
        if self._initialized:
            return
        self.driver = get_graph_driver()
        init_constraints(self.driver)
        self._initialized = True
        logger.info("[GraphExplorerService] Connected and constraints ready.")
        
    def get_project_graph(self, project_name: str) -> dict:
        try:
            with self.driver.session() as session:
                records = session.execute_read(queries.find_project_graph, project_name)
                raw_graph = build_graph_payload(records)
                return format_for_react_flow(raw_graph)
        except Exception as e:
            logger.error(f"[GraphExplorerService] Error fetching project graph: {e}")
            return {"nodes": [], "edges": []}
            
    def get_component_graph(self, component_name: str) -> dict:
        try:
            with self.driver.session() as session:
                records = session.execute_read(queries.find_component_graph, component_name)
                raw_graph = build_graph_payload(records)
                return format_for_react_flow(raw_graph)
        except Exception as e:
            logger.error(f"[GraphExplorerService] Error fetching component graph: {e}")
            return {"nodes": [], "edges": []}
            
    def get_team_graph(self, team_name: str) -> dict:
        try:
            with self.driver.session() as session:
                records = session.execute_read(queries.find_team_graph, team_name)
                raw_graph = build_graph_payload(records)
                return format_for_react_flow(raw_graph)
        except Exception as e:
            logger.error(f"[GraphExplorerService] Error fetching team graph: {e}")
            return {"nodes": [], "edges": []}
            
    def get_user_graph(self, user_email: str) -> dict:
        try:
            with self.driver.session() as session:
                records = session.execute_read(queries.find_user_graph, user_email)
                raw_graph = build_graph_payload(records)
                return format_for_react_flow(raw_graph)
        except Exception as e:
            logger.error(f"[GraphExplorerService] Error fetching user graph: {e}")
            return {"nodes": [], "edges": []}
            
    def search_graph(self, query_str: str) -> dict:
        try:
            with self.driver.session() as session:
                records = session.execute_read(queries.search_graph, query_str)
                # Form list of node objects
                nodes = []
                for r in records:
                    node = r.get("n")
                    if node:
                        nodes.append(format_node_record(node))
                return {"nodes": nodes}
        except Exception as e:
            logger.error(f"[GraphExplorerService] Error searching graph: {e}")
            return {"nodes": []}
            
    def ingest_project(self, user_email: str, team_name: str, project_name: str, package_data: dict, audit_logs: list) -> bool:
        try:
            with self.driver.session() as session:
                session.execute_write(
                    ingest_complete_project_graph, 
                    user_email, 
                    team_name, 
                    project_name, 
                    package_data, 
                    audit_logs
                )
            logger.info(f"[GraphExplorerService] Successfully ingested complete EKG project: '{project_name}'.")
            return True
        except Exception as e:
            logger.error(f"[GraphExplorerService] EKG Ingestion failed for project '{project_name}': {e}")
            return False

def format_node_record(node) -> dict:
    from backend.graph.graph_builder import get_node_id, format_node
    return format_node(node)
