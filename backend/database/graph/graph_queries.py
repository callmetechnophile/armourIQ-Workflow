def find_similar_projects(tx, project_name: str):
    query = """
    MATCH (p:Project {name: $project_name})
    MATCH (p)-[:USES|HAS_BOM]->(shared:Component)
    MATCH (other:Project)-[:USES|HAS_BOM]->(shared)
    WHERE other <> p
    RETURN other.name AS name, count(shared) AS score, collect(shared.name) AS shared_items
    ORDER BY score DESC LIMIT 5
    """
    res = tx.run(query, project_name=project_name)
    return [dict(record) for record in res]

def find_alternative_components(tx, component_name: str):
    query = """
    MATCH (c:Component {name: $component_name})-[:ALTERNATIVE_TO]->(alt:Component)
    RETURN alt.name AS name, alt.category AS category, alt.cost AS cost, alt.notes AS notes
    """
    res = tx.run(query, component_name=component_name)
    return [dict(record) for record in res]

def find_compatible_components(tx, component_name: str):
    query = """
    MATCH (c:Component {name: $component_name})-[:CONNECTED_TO]-(comp:Component)
    RETURN comp.name AS name, comp.category AS category
    """
    res = tx.run(query, component_name=component_name)
    return [dict(record) for record in res]

def find_component_datasheet(tx, component_name: str):
    query = """
    MATCH (c:Component {name: $component_name})-[:HAS_DATASHEET]->(d:Datasheet)
    RETURN d.title AS title, d.manufacturer AS manufacturer, d.url AS url, d.revision AS revision, d.document_type AS document_type
    """
    res = tx.run(query, component_name=component_name)
    return [dict(record) for record in res]

def find_component_failure_modes(tx, component_name: str):
    query = """
    MATCH (c:Component {name: $component_name})-[:HAS_FAILURE_MODE]->(f:FailureMode)
    RETURN f.name AS name, f.severity AS severity, f.mitigation AS mitigation
    """
    res = tx.run(query, component_name=component_name)
    return [dict(record) for record in res]

def find_vendor_relationships(tx, component_name: str):
    query = """
    MATCH (c:Component {name: $component_name})<-[:SELLS]-(v:Vendor)
    OPTIONAL MATCH (v)-[:LOCATED_IN]->(city:City)
    OPTIONAL MATCH (v)-[:OFFERS]->(ship:ShippingMethod)
    RETURN v.name AS vendor, c.cost AS cost, city.name AS location, collect(ship.name) AS shipping_methods
    """
    res = tx.run(query, component_name=component_name)
    return [dict(record) for record in res]

def find_related_research(tx, project_name: str):
    query = """
    MATCH (p:Project {name: $project_name})-[:SUPPORTED_BY]->(paper:ResearchPaper)
    OPTIONAL MATCH (paper)-[:CONTRADICTS]-(contradicted:ResearchPaper)
    RETURN paper.title AS paper_title, paper.url AS url, collect(contradicted.title) AS contradicted_papers
    """
    res = tx.run(query, project_name=project_name)
    return [dict(record) for record in res]

def find_protocol_dependencies(tx, protocol_name: str):
    query = """
    MATCH (c:Component)-[:COMMUNICATES_VIA]->(p:Protocol {name: $protocol_name})
    RETURN c.name AS component, c.category AS category
    """
    res = tx.run(query, protocol_name=protocol_name)
    return [dict(record) for record in res]

def find_power_dependencies(tx, component_name: str):
    query = """
    MATCH (c:Component {name: $component_name})-[:POWERED_BY]->(b:Battery)
    RETURN b.name AS battery, b.capacity AS capacity, b.voltage AS voltage
    """
    res = tx.run(query, component_name=component_name)
    return [dict(record) for record in res]

def find_component_connections(tx, component_name: str):
    query = """
    MATCH (c1:Component {name: $component_name})-[:HAS_PIN]->(p1:Pin)-[:CONNECTED_TO]-(p2:Pin)<-[:HAS_PIN]-(c2:Component)
    RETURN p1.name AS source_pin, p2.name AS target_pin, c2.name AS connected_component
    """
    res = tx.run(query, component_name=component_name)
    return [dict(record) for record in res]

def find_project_graph(tx, project_name: str):
    query = """
    MATCH (p:Project {name: $project_name})
    OPTIONAL MATCH (p)-[r]-(n)
    RETURN p AS source_node, type(r) AS rel_type, n AS target_node
    """
    res = tx.run(query, project_name=project_name)
    
    nodes = []
    edges = []
    seen_nodes = set()
    project_added = False
    
    for record in res:
        # Convert to dictionary representation safely
        source = record.get("source_node")
        rel_type = record.get("rel_type")
        target = record.get("target_node")
        
        if source:
            source_id = f"node_{source.element_id}" if hasattr(source, "element_id") else (f"node_{source.id}" if hasattr(source, "id") else f"node_project_{project_name}")
            source_labels = list(source.labels) if hasattr(source, "labels") else ["Project"]
            source_props = dict(source) if not isinstance(source, dict) else source
            if source_id not in seen_nodes:
                nodes.append({
                    "id": source_id,
                    "label": source_props.get("name", project_name),
                    "type": source_labels[0],
                    "properties": source_props
                })
                seen_nodes.add(source_id)
                project_added = True
                
        if target:
            target_id = f"node_{target.element_id}" if hasattr(target, "element_id") else (f"node_{target.id}" if hasattr(target, "id") else f"node_{target.get('name', 'node')}")
            target_labels = list(target.labels) if hasattr(target, "labels") else ["Node"]
            target_props = dict(target) if not isinstance(target, dict) else target
            if target_id not in seen_nodes:
                nodes.append({
                    "id": target_id,
                    "label": target_props.get("name") or target_props.get("title") or target_id,
                    "type": target_labels[0],
                    "properties": target_props
                })
                seen_nodes.add(target_id)
                
            if source and rel_type:
                edges.append({
                    "source": source_id,
                    "target": target_id,
                    "type": rel_type
                })
                
    if not project_added:
        nodes.append({
            "id": f"node_project_{project_name}",
            "label": project_name,
            "type": "Project",
            "properties": {"name": project_name}
        })
        
    return {"nodes": nodes, "edges": edges}
