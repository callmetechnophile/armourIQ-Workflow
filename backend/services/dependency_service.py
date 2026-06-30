from typing import List, Dict, Any

def generate_dependency_graph(components: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Constructs project dependency relationships (nodes and edges)
    categorized by power, signal, mechanical, and communication.
    """
    nodes = []
    edges = []
    
    # Identify key nodes based on name matching
    has_battery = False
    battery_id = ""
    
    has_controller = False
    controller_id = ""
    
    has_driver = False
    driver_id = ""
    
    peripherals = []
    mechanicals = []
    
    for idx, comp in enumerate(components):
        name = comp.get("component") or comp.get("name", "")
        cat = comp.get("category", "")
        node_id = f"node_{idx}"
        
        node_type = "default"
        if "battery" in name.lower() or "lipo" in name.lower() or "power supply" in name.lower():
            has_battery = True
            battery_id = node_id
            node_type = "source"
        elif "esp32" in name.lower() or "arduino" in name.lower() or "pixhawk" in name.lower():
            has_controller = True
            controller_id = node_id
            node_type = "controller"
        elif "pca9685" in name.lower() or "driver" in name.lower() or "esc" in name.lower():
            has_driver = True
            driver_id = node_id
            node_type = "driver"
        elif "filament" in name.lower() or "acrylic" in name.lower() or "frame" in name.lower() or "structure" in name.lower():
            mechanicals.append((node_id, name))
            node_type = "mechanical"
        else:
            peripherals.append((node_id, name, cat))
            node_type = "peripheral"
            
        nodes.append({
            "id": node_id,
            "label": name,
            "type": node_type,
            "category": cat
        })
        
    # Build Edges based on component relationships
    if has_battery:
        # Power goes to controller
        if has_controller:
            edges.append({
                "id": f"e_bat_ctrl",
                "source": battery_id,
                "target": controller_id,
                "type": "power",
                "label": "7.4V Power Rail"
            })
        # Power goes to driver
        if has_driver:
            edges.append({
                "id": f"e_bat_drv",
                "source": battery_id,
                "target": driver_id,
                "type": "power",
                "label": "High-Current Servo Rail"
            })
            
    if has_controller:
        # Communication to driver
        if has_driver:
            edges.append({
                "id": f"e_ctrl_drv",
                "source": controller_id,
                "target": driver_id,
                "type": "communication",
                "label": "I2C SDA/SCL"
            })
            
        # Signal / Communication to peripherals
        for p_id, p_name, p_cat in peripherals:
            if "sensor" in p_name.lower():
                edges.append({
                    "id": f"e_ctrl_{p_id}",
                    "source": p_id,
                    "target": controller_id,
                    "type": "signal",
                    "label": "Analog Bend Input"
                })
            elif not has_driver: # controller drives peripherals directly if driver is absent
                edges.append({
                    "id": f"e_ctrl_{p_id}",
                    "source": controller_id,
                    "target": p_id,
                    "type": "signal",
                    "label": "Direct PWM Control"
                })
                
    if has_driver:
        # Driver drives actuators/motors
        for p_id, p_name, p_cat in peripherals:
            if "servo" in p_name.lower() or "motor" in p_name.lower():
                edges.append({
                    "id": f"e_drv_{p_id}",
                    "source": driver_id,
                    "target": p_id,
                    "type": "signal",
                    "label": "PWM Duty Cycle"
                })
                
    # Mechanical linkages
    for m_id, m_name in mechanicals:
        for p_id, p_name, p_cat in peripherals:
            if "servo" in p_name.lower() or "sensor" in p_name.lower():
                edges.append({
                    "id": f"e_mech_{m_id}_{p_id}",
                    "source": m_id,
                    "target": p_id,
                    "type": "mechanical",
                    "label": "Mounting Link"
                })
                
    return {
        "nodes": nodes,
        "edges": edges
    }
