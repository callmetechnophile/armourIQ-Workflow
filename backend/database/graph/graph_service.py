import logging
from backend.database.graph.graph_connection import get_graph_driver
from backend.database.graph.graph_schema import init_constraints
import backend.database.graph.graph_queries as queries
from backend.database.graph.graph_loader import ingest_project_graph

logger = logging.getLogger("GraphService")

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
        logger.info("[GraphService] Initialized and constraint rules established.")
        
    def run_read_query(self, query_name: str, params: dict = None):
        params = params or {}
        # Resolve query function
        fn = getattr(queries, query_name, None)
        if not fn:
            logger.error(f"[GraphService] Unknown query name: {query_name}")
            return []
            
        try:
            with self.driver.session() as session:
                return session.execute_read(fn, **params)
        except Exception as e:
            logger.error(f"[GraphService] Error executing read query '{query_name}': {e}")
            return []
            
    def run_write_query(self, query_name: str, params: dict = None):
        params = params or {}
        fn = getattr(queries, query_name, None)
        if not fn:
            logger.error(f"[GraphService] Unknown query name: {query_name}")
            return []
            
        try:
            with self.driver.session() as session:
                return session.execute_write(fn, **params)
        except Exception as e:
            logger.error(f"[GraphService] Error executing write query '{query_name}': {e}")
            return []
            
    def ingest_project(self, project_name: str, package_data: dict):
        try:
            with self.driver.session() as session:
                session.execute_write(ingest_project_graph, project_name, package_data)
            logger.info(f"[GraphService] Ingested project graph for '{project_name}'.")
            return True
        except Exception as e:
            logger.error(f"[GraphService] Ingest failed for project '{project_name}': {e}")
            return False
