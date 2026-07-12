import time
from backend.database.graph.graph_schema import (
    PROJECT, COMPONENT, TIMELINE, TASK, PROTOCOL, PIN, RESEARCH_PAPER,
    DATASHEET, VENDOR, FAILURE_MODE, OPTIMIZATION, BATTERY, MANUFACTURER
)

def ingest_project_graph(tx, project_name: str, package_data: dict):
    # 1. Ingest Project
    tx.run(
        "MERGE (p:Project {name: $name}) "
        "SET p.intent = $intent, p.timestamp = $timestamp",
        name=project_name,
        intent=package_data.get("intent", ""),
        timestamp=str(time.time())
    )
    
    # 2. Ingest Timeline & Tasks
    gantt = package_data.get("gantt", [])
    roadmap = package_data.get("roadmap", [])
    days_total = sum(r.get("duration_days", 0) for r in roadmap) if roadmap else 22
    
    tx.run(
        "MATCH (p:Project {name: $project_name}) "
        "MERGE (t:Timeline {id: $t_id}) "
        "SET t.days = $days, t.project = $project_name "
        "MERGE (p)-[:HAS_TIMELINE]->(t)",
        project_name=project_name,
        t_id=f"timeline_{project_name}",
        days=days_total
    )
    
    for task in gantt:
        tx.run(
            "MATCH (p:Project {name: $project_name}) "
            "MERGE (tsk:Task {id: $task_id}) "
            "SET tsk.name = $name, tsk.start = $start, tsk.end = $end, tsk.progress = $progress, tsk.project = $project_name "
            "MERGE (p)-[:HAS_TASK]->(tsk)",
            project_name=project_name,
            task_id=task.get("id"),
            name=task.get("name"),
            start=task.get("start"),
            end=task.get("end"),
            progress=task.get("progress", 0)
        )
        
    # 3. Ingest Components & Sourcing Info
    components = package_data.get("components", [])
    for comp in components:
        comp_name = comp.get("component") or comp.get("name")
        if not comp_name:
            continue
            
        category = comp.get("category", "")
        cost = comp.get("final_cost") or comp.get("cost") or 0.0
        vendor_name = comp.get("optimal_vendor") or comp.get("vendor") or "Generic Vendor"
        
        # Determine specific labels
        cat_lower = category.lower()
        name_lower = comp_name.lower()
        
        labels = ["Component"]
        if "controller" in cat_lower or "esp32" in name_lower or "arduino" in name_lower or "raspberry" in name_lower or "mcu" in cat_lower:
            labels.append("Microcontroller")
            labels.append("ElectronicComponent")
        elif "sensor" in cat_lower or "flex" in name_lower or "ultrasonic" in name_lower:
            labels.append("Sensor")
            labels.append("ElectronicComponent")
        elif "actuator" in cat_lower or "servo" in name_lower or "motor" in name_lower:
            labels.append("Actuator")
            labels.append("Motor")
            labels.append("ElectronicComponent")
        elif "battery" in name_lower or "power" in cat_lower or "lipo" in name_lower:
            labels.append("Battery")
            labels.append("ElectronicComponent")
        elif "frame" in cat_lower or "acrylic" in name_lower or "filament" in name_lower or "pla" in name_lower or "abs" in name_lower:
            labels.append("StructuralComponent")
            labels.append("MechanicalComponent")
        else:
            labels.append("StructuralComponent")
            
        # Merge basic component node
        label_clause = ":".join(labels)
        query = (
            f"MERGE (c:{label_clause} {{name: $name}}) "
            f"SET c.category = $category, c.cost = $cost"
        )
        tx.run(query, name=comp_name, category=category, cost=cost)
        
        # Link Project -> Component
        tx.run(
            "MATCH (p:Project {name: $project_name}), (c:Component {name: $comp_name}) "
            "MERGE (p)-[:USES]->(c) "
            "MERGE (p)-[:HAS_BOM]->(c)",
            project_name=project_name,
            comp_name=comp_name
        )
        
        # Ingest Vendor Sells Component
        tx.run(
            "MATCH (c:Component {name: $comp_name}) "
            "MERGE (v:Vendor {name: $vendor_name}) "
            "MERGE (v)-[:SELLS]->(c) "
            "MERGE (c)-[:AVAILABLE_AT]->(v)",
            comp_name=comp_name,
            vendor_name=vendor_name
        )
        
        # 4. Ingest Datasheets
        # Look up datasheet for this component in package_data datasheets
        datasheets_list = package_data.get("datasheets", [])
        # Sometimes datasheets list is list of dicts, let's find the matching one
        matching_ds = None
        for ds in datasheets_list:
            if isinstance(ds, dict) and (ds.get("component") == comp_name or ds.get("name") == comp_name):
                matching_ds = ds
                break
                
        if matching_ds:
            manufacturer = matching_ds.get("manufacturer") or "Unknown Manufacturer"
            tx.run(
                "MATCH (c:Component {name: $comp_name}) "
                "MERGE (d:Datasheet {url: $url}) "
                "SET d.title = $title, d.manufacturer = $manufacturer, d.revision = $revision, d.document_type = $doc_type "
                "MERGE (c)-[:HAS_DATASHEET]->(d) "
                "MERGE (m:Manufacturer {name: $manufacturer}) "
                "MERGE (c)-[:MANUFACTURED_BY]->(m)",
                comp_name=comp_name,
                url=matching_ds.get("url") or matching_ds.get("datasheet_url") or f"https://datasheets.com/{comp_name}",
                title=matching_ds.get("title") or f"{comp_name} Datasheet",
                manufacturer=manufacturer,
                revision=matching_ds.get("revision") or "Rev 1.0",
                doc_type=matching_ds.get("document_type") or "PDF Datasheet"
            )
            
        # 5. Ingest Alternative Components
        alternatives = comp.get("alternatives", [])
        for alt in alternatives:
            alt_name = alt.get("alternative") or alt.get("name")
            if not alt_name:
                continue
            alt_cost = alt.get("final_cost") or alt.get("cost") or 0.0
            tx.run(
                "MATCH (c:Component {name: $comp_name}) "
                "MERGE (alt:Component {name: $alt_name}) "
                "SET alt.cost = $alt_cost "
                "MERGE (c)-[:ALTERNATIVE_TO]->(alt)",
                comp_name=comp_name,
                alt_name=alt_name,
                alt_cost=alt_cost
            )
            
            # Ingest Optimization receipt linking
            opt_id = f"opt_{project_name}_{comp_name}_{alt_name}"
            tx.run(
                "MATCH (p:Project {name: $project_name}) "
                "MERGE (o:Optimization {id: $opt_id}) "
                "SET o.component = $comp_name, o.alternative = $alt_name, o.project = $project_name "
                "MERGE (p)-[:OPTIMIZED_BY]->(o)",
                project_name=project_name,
                opt_id=opt_id,
                comp_name=comp_name,
                alt_name=alt_name
            )

        # 6. Ingest Failure Modes
        # Attach default failure modes based on component category
        fms = []
        if "controller" in cat_lower:
            fms = [
                {"name": "GPIO short-circuit", "severity": "High", "mitigation": "Install series resistors on I/O lines."},
                {"name": "Voltage spike on 3.3V line", "severity": "Critical", "mitigation": "Use stable voltage regulators and TVS diodes."}
            ]
        elif "battery" in name_lower or "power" in cat_lower:
            fms = [
                {"name": "Thermal runaway", "severity": "Critical", "mitigation": "Implement battery management system (BMS) with temperature monitoring."},
                {"name": "Deep discharge", "severity": "High", "mitigation": "Use low-voltage cutoff circuits."}
            ]
        elif "sensor" in cat_lower:
            fms = [
                {"name": "Signal noise interference", "severity": "Medium", "mitigation": "Use shielded cables and decoupling capacitors."}
            ]
            
        for fm in fms:
            tx.run(
                "MATCH (c:Component {name: $comp_name}) "
                "MERGE (f:FailureMode {id: $fm_id}) "
                "SET f.name = $name, f.severity = $severity, f.mitigation = $mitigation "
                "MERGE (c)-[:HAS_FAILURE_MODE]->(f)",
                comp_name=comp_name,
                fm_id=f"fm_{comp_name}_{fm['name']}".replace(" ", "_"),
                name=fm["name"],
                severity=fm["severity"],
                mitigation=fm["mitigation"]
            )

    # 7. Ingest Protocols & Pins
    pin_mapping = package_data.get("pin_mapping", {})
    # Usually pin_mapping is a dictionary mapping components to pins or list of pins
    # Let's inspect potential formats
    if isinstance(pin_mapping, dict):
        mapping_entries = pin_mapping.get("pins") or pin_mapping.get("mapping") or []
        if not isinstance(mapping_entries, list):
            mapping_entries = []
        for entry in mapping_entries:
            comp_name = entry.get("component") or entry.get("device")
            pin_name = entry.get("pin") or entry.get("gpio")
            protocol = entry.get("protocol") or entry.get("bus") or "GPIO"
            
            if comp_name and pin_name:
                tx.run(
                    "MATCH (c:Component {name: $comp_name}) "
                    "MERGE (proto:Protocol {name: $protocol}) "
                    "MERGE (c)-[:COMMUNICATES_VIA]->(proto) "
                    "MERGE (pin:Pin {id: $pin_id}) "
                    "SET pin.name = $pin_name, pin.component = $comp_name "
                    "MERGE (c)-[:HAS_PIN]->(pin)",
                    comp_name=comp_name,
                    protocol=protocol,
                    pin_id=f"pin_{comp_name}_{pin_name}".replace(" ", "_"),
                    pin_name=pin_name
                )
                
    # 8. Ingest Wiring Connections (CONNECTED_TO)
    wiring = package_data.get("wiring_diagram", {})
    if isinstance(wiring, dict):
        connections = wiring.get("connections") or wiring.get("wires") or []
        for conn in connections:
            from_comp = conn.get("from_component") or conn.get("source")
            from_pin = conn.get("from_pin") or conn.get("source_pin")
            to_comp = conn.get("to_component") or conn.get("target")
            to_pin = conn.get("to_pin") or conn.get("target_pin")
            
            if from_comp and to_comp:
                # Link components directly
                tx.run(
                    "MATCH (c1:Component {name: $from_comp}), (c2:Component {name: $to_comp}) "
                    "MERGE (c1)-[:CONNECTED_TO]->(c2)",
                    from_comp=from_comp,
                    to_comp=to_comp
                )
                
                # Link individual pins
                if from_pin and to_pin:
                    p1_id = f"pin_{from_comp}_{from_pin}".replace(" ", "_")
                    p2_id = f"pin_{to_comp}_{to_pin}".replace(" ", "_")
                    tx.run(
                        "MERGE (p1:Pin {id: $p1_id}) SET p1.name = $p1_name, p1.component = $from_comp "
                        "MERGE (p2:Pin {id: $p2_id}) SET p2.name = $p2_name, p2.component = $to_comp "
                        "MERGE (p1)-[:CONNECTED_TO]->(p2)",
                        p1_id=p1_id,
                        p1_name=from_pin,
                        from_comp=from_comp,
                        p2_id=p2_id,
                        p2_name=to_pin,
                        to_comp=to_comp
                    )

    # 9. Ingest Power dependencies
    power_analysis = package_data.get("power_analysis", {})
    if isinstance(power_analysis, dict):
        rails = power_analysis.get("voltage_rails") or power_analysis.get("rails") or []
        battery_name = power_analysis.get("battery_component") or "LiPo Battery Pack"
        
        # Merge battery node
        tx.run(
            "MERGE (b:Battery:Component {name: $name}) "
            "SET b.capacity = $capacity, b.voltage = $voltage, b.category = 'Power Source'",
            name=battery_name,
            capacity=power_analysis.get("battery_capacity", "2200mAh"),
            voltage=power_analysis.get("nominal_voltage", "7.4V")
        )
        
        # Link battery to project
        tx.run(
            "MATCH (p:Project {name: $project_name}), (b:Component {name: $battery_name}) "
            "MERGE (p)-[:USES]->(b) "
            "MERGE (p)-[:HAS_BOM]->(b)",
            project_name=project_name,
            battery_name=battery_name
        )
        
        for rail in rails:
            rail_name = rail.get("rail") or rail.get("voltage") or "5V Rail"
            tx.run(
                "MERGE (pr:PowerRail {name: $rail_name})",
                rail_name=rail_name
            )
            
            # Connect components to the rail and battery
            rail_comps = rail.get("components") or []
            for rc in rail_comps:
                tx.run(
                    "MATCH (c:Component {name: $rc_name}) "
                    "MERGE (pr:PowerRail {name: $rail_name}) "
                    "MERGE (b:Battery {name: $battery_name}) "
                    "MERGE (c)-[:REQUIRES]->(pr) "
                    "MERGE (c)-[:POWERED_BY]->(b)",
                    rc_name=rc,
                    rail_name=rail_name,
                    battery_name=battery_name
                )

    # 10. Ingest Research Papers
    papers = package_data.get("papers", [])
    for paper in papers:
        title = paper.get("title")
        if not title:
            continue
            
        url = paper.get("url") or paper.get("pdf_url") or f"https://arxiv.org/abs/{title.replace(' ', '_')}"
        year = paper.get("publish_year") or paper.get("year") or 2024
        score = paper.get("score") or 85
        
        tx.run(
            "MATCH (p:Project {name: $project_name}) "
            "MERGE (rp:ResearchPaper {title: $title}) "
            "SET rp.url = $url, rp.publish_year = $year, rp.score = $score "
            "MERGE (p)-[:SUPPORTED_BY]->(rp)",
            project_name=project_name,
            title=title,
            url=url,
            year=year,
            score=score
        )
        
    # 11. Ingest Contradictions
    contradictions = package_data.get("contradictions", [])
    if isinstance(contradictions, list):
        for con in contradictions:
            p1 = con.get("paper1") or con.get("paper1_title")
            p2 = con.get("paper2") or con.get("paper2_title")
            if p1 and p2:
                tx.run(
                    "MERGE (rp1:ResearchPaper {title: $p1}) "
                    "MERGE (rp2:ResearchPaper {title: $p2}) "
                    "MERGE (rp1)-[:CONTRADICTS]-(rp2)",
                    p1=p1,
                    p2=p2
                )
