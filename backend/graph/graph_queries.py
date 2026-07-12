def find_project_graph(tx, project_name: str):
    query = """
    MATCH (p:Project {name: $project_name})
    OPTIONAL MATCH (p)-[r]-(n)
    RETURN p AS source_node, type(r) AS rel_type, n AS target_node
    """
    res = tx.run(query, project_name=project_name)
    return [dict(record) for record in res]

def find_component_graph(tx, component_name: str):
    query = """
    MATCH (c:Component {name: $component_name})
    OPTIONAL MATCH (c)-[r]-(n)
    RETURN c AS source_node, type(r) AS rel_type, n AS target_node
    """
    res = tx.run(query, component_name=component_name)
    return [dict(record) for record in res]

def find_team_graph(tx, team_name: str):
    query = """
    MATCH (t:Team {name: $team_name})
    OPTIONAL MATCH (t)-[r]-(n)
    RETURN t AS source_node, type(r) AS rel_type, n AS target_node
    """
    res = tx.run(query, team_name=team_name)
    return [dict(record) for record in res]

def find_user_graph(tx, user_email: str):
    query = """
    MATCH (u:User {email: $user_email})
    OPTIONAL MATCH (u)-[r]-(n)
    RETURN u AS source_node, type(r) AS rel_type, n AS target_node
    """
    res = tx.run(query, user_email=user_email)
    return [dict(record) for record in res]

def search_graph(tx, query_str: str):
    query = """
    MATCH (n)
    WHERE toLower(n.name) CONTAINS toLower($query_str) OR toLower(n.title) CONTAINS toLower($query_str)
    RETURN n LIMIT 50
    """
    res = tx.run(query, query_str=query_str)
    return [dict(record) for record in res]
