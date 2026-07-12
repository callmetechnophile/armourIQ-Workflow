def format_for_react_flow(raw_graph: dict) -> dict:
    nodes = raw_graph.get("nodes", [])
    edges = raw_graph.get("edges", [])
    
    formatted_nodes = []
    formatted_edges = []
    
    # Grid spacing helpers
    width = 900
    height = 550
    
    for idx, node in enumerate(nodes):
        n_type = node.get("type", "Component")
        n_id = node.get("id")
        
        # Default positioning so React Flow has an initial grid layout
        row = idx // 4
        col = idx % 4
        
        # Categorized color configuration for React Flow styling
        color_info = get_react_flow_node_styles(n_type)
        
        formatted_nodes.append({
            "id": n_id,
            "type": "customNode", # custom node type for rendering custom icons
            "position": {
                "x": 80 + col * 210 + (row % 2) * 30,
                "y": 80 + row * 120
            },
            "data": {
                "label": node.get("label", "Node"),
                "type": n_type,
                "properties": node.get("properties", {}),
                "icon": color_info.get("icon", "Layers"),
                "borderColor": color_info.get("borderColor", "#64748b"),
                "bgColor": color_info.get("bgColor", "#1e293b15")
            }
        })
        
    for edge in edges:
        formatted_edges.append({
            "id": f"edge_{edge['source']}_{edge['target']}",
            "source": edge["source"],
            "target": edge["target"],
            "label": edge["type"],
            "animated": edge["type"] in ("USES", "POWERED_BY", "DELEGATES_TO"),
            "style": { "stroke": get_edge_stroke_color(edge["type"]), "strokeWidth": 1.5 }
        })
        
    return {
        "nodes": formatted_nodes,
        "edges": formatted_edges
    }

def get_react_flow_node_styles(n_type: str) -> dict:
    # Set icons and border colors based on node type
    if n_type == "Project":
        return {"borderColor": "#eab308", "bgColor": "#eab30815", "icon": "Layers"}
    elif n_type == "User":
        return {"borderColor": "#3b82f6", "bgColor": "#3b82f615", "icon": "User"}
    elif n_type == "Team":
        return {"borderColor": "#a855f7", "bgColor": "#a855f715", "icon": "Users"}
    elif n_type == "Component":
        return {"borderColor": "#6366f1", "bgColor": "#6366f115", "icon": "Cpu"}
    elif n_type == "Vendor":
        return {"borderColor": "#d946ef", "bgColor": "#d946ef15", "icon": "Store"}
    elif n_type == "ResearchPaper":
        return {"borderColor": "#ec4899", "bgColor": "#ec489915", "icon": "BookOpen"}
    elif n_type == "Datasheet":
        return {"borderColor": "#14b8a6", "bgColor": "#14b8a615", "icon": "FileText"}
    elif n_type == "Battery":
        return {"borderColor": "#f97316", "bgColor": "#f9731615", "icon": "Zap"}
    elif n_type == "Sensor":
        return {"borderColor": "#10b981", "bgColor": "#10b98115", "icon": "Activity"}
    elif n_type == "Protocol":
        return {"borderColor": "#06b6d4", "bgColor": "#06b6d415", "icon": "Radio"}
    elif n_type == "Code":
        return {"borderColor": "#0284c7", "bgColor": "#0284c715", "icon": "Terminal"}
    elif n_type == "Agent":
        return {"borderColor": "#0891b2", "bgColor": "#0891b215", "icon": "Sparkles"}
    elif n_type == "FailureMode":
        return {"borderColor": "#ef4444", "bgColor": "#ef444415", "icon": "AlertTriangle"}
    else:
        return {"borderColor": "#64748b", "bgColor": "#64748b15", "icon": "HelpCircle"}

def get_edge_stroke_color(rel_type: str) -> str:
    if rel_type in ("POWERED_BY", "POWER_RAIL"):
        return "#f97316" # Orange
    elif rel_type in ("CONNECTED_TO", "COMMUNICATES_VIA"):
        return "#06b6d4" # Cyan
    elif rel_type in ("DELEGATES_TO", "GENERATED"):
        return "#a855f7" # Purple
    elif rel_type in ("SUPPORTED_BY", "SUPPORTS"):
        return "#ec4899" # Pink
    elif rel_type == "CONTRADICTS":
        return "#ef4444" # Red
    return "#475569" # Default dark slate
