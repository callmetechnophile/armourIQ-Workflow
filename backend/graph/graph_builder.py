def get_node_id(node) -> str:
    if hasattr(node, "element_id"):
        return f"node_{node.element_id}"
    elif hasattr(node, "id"):
        return f"node_{node.id}"
    elif isinstance(node, dict):
        return f"node_{node.get('name') or node.get('title') or 'node'}"
    return "node_unknown"

def format_node(node) -> dict:
    labels = list(node.labels) if hasattr(node, "labels") else ["Node"]
    props = dict(node) if not isinstance(node, dict) else node
    name = props.get("name") or props.get("title") or "Node"
    return {
        "id": get_node_id(node),
        "label": name,
        "type": labels[0] if labels else "Node",
        "properties": props
    }

def build_graph_payload(records: list) -> dict:
    nodes = {}
    edges = []
    
    for r in records:
        source = r.get("source_node")
        rel_type = r.get("rel_type")
        target = r.get("target_node")
        
        if source:
            source_id = get_node_id(source)
            if source_id not in nodes:
                nodes[source_id] = format_node(source)
                
        if target:
            target_id = get_node_id(target)
            if target_id not in nodes:
                nodes[target_id] = format_node(target)
                
            if source and rel_type:
                edges.append({
                    "source": source_id,
                    "target": target_id,
                    "type": rel_type
                })
                
    return {"nodes": list(nodes.values()), "edges": edges}
