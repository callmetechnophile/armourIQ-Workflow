import os
import logging

logger = logging.getLogger("GraphConnection")

class MockRecord:
    def __init__(self, data):
        self._data = data
    def __getitem__(self, key):
        return self._data.get(key)
    def get(self, key, default=None):
        return self._data.get(key, default)
    def data(self):
        return self._data
    def items(self):
        return self._data.items()

class MockResult:
    def __init__(self, records=None):
        self._records = [MockRecord(r) if isinstance(r, dict) else r for r in (records or [])]
    def __iter__(self):
        return iter(self._records)
    def data(self):
        return [r.data() if isinstance(r, MockRecord) else r for r in self._records]

class MockTransaction:
    def run(self, query, **kwargs):
        logger.info(f"[MockNeo4j TX] Executing query: {query}")
        return MockResult()

class MockSession:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    def run(self, query, **kwargs):
        logger.info(f"[MockNeo4j Session] Executing query: {query}")
        return MockResult()
    def execute_read(self, transaction_fn, *args, **kwargs):
        return transaction_fn(MockTransaction(), *args, **kwargs)
    def execute_write(self, transaction_fn, *args, **kwargs):
        return transaction_fn(MockTransaction(), *args, **kwargs)
    def close(self):
        pass

class MockDriver:
    def verify_connectivity(self):
        logger.warning("[MockNeo4j] Simulated connection success.")
    def session(self, **kwargs):
        return MockSession()
    def close(self):
        pass

def get_graph_driver():
    uri = os.environ.get("AURA_URI")
    username = os.environ.get("AURA_USERNAME")
    password = os.environ.get("AURA_PASSWORD")
    
    if not uri or not username or not password:
        logger.warning("[GraphConnection] AURA_URI, AURA_USERNAME, or AURA_PASSWORD is not set. Falling back to MockDriver.")
        return MockDriver()
        
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(uri, auth=(username, password))
        # Verify connection
        driver.verify_connectivity()
        logger.info("[GraphConnection] Successfully connected to AuraDB.")
        return driver
    except Exception as e:
        logger.error(f"[GraphConnection] Failed to connect to AuraDB: {e}. Falling back to MockDriver.")
        return MockDriver()
