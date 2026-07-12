import time
from backend.graph.graph_models import (
    USER, TEAM, PROJECT, COMPONENT, VENDOR, RESEARCH_PAPER,
    DATASHEET, BATTERY, PROTOCOL, PIN, FAILURE_MODE
)

def ingest_complete_project_graph(tx, user_email: str, team_name: str, project_name: str, package_data: dict, audit_logs: list):
    # 1. Ingest User
    user_email = user_email or "engineer@armourline.io"
    tx.run(
        "MERGE (u:User {email: $email}) "
        "SET u.name = $name",
        email=user_email,
        name=user_email.split('@')[0].capitalize()
    )

    # 2. Ingest Team
    team_name = team_name or "Engineering Team"
    tx.run(
        "MERGE (t:Team {name: $name}) "
        "SET t.created_at = $created_at",
        name=team_name,
        created_at=str(time.time())
    )

    # Link User Member/Owner of Team
    tx.run(
        "MATCH (u:User {email: $email}), (t:Team {name: $team_name}) "
        "MERGE (u)-[:MEMBER_OF]->(t) "
        "MERGE (u)-[:OWNER_OF]->(t) "
        "MERGE (u)-[:ENGINEER_IN]->(t)",
        email=user_email,
        team_name=team_name
    )

    # 3. Ingest Project
    tx.run(
        "MERGE (p:Project {name: $name}) "
        "SET p.intent = $intent, p.timestamp = $timestamp",
        name=project_name,
        intent=package_data.get("intent", ""),
        timestamp=str(time.time())
    )

    # Link User created Project, Team owns Project
    tx.run(
        "MATCH (u:User {email: $email}), (t:Team {name: $team_name}), (p:Project {name: $project_name}) "
        "MERGE (u)-[:CREATED]->(p) "
        "MERGE (u)-[:OWNS]->(p) "
        "MERGE (t)-[:OWNS]->(p) "
        "MERGE (p)-[:SHARED_WITH]->(t)",
        email=user_email,
        team_name=team_name,
        project_name=project_name
    )

    # 4. Ingest AI Agents & Delegation Chain (Receipts)
    agents_map = {}
    for log in audit_logs:
        agent_name = log.get("agent")
        action = log.get("action")
        receipt_id = log.get("receipt_id")
        parent_id = log.get("parent_receipt_id")

        if agent_name:
            tx.run(
                "MERGE (a:Agent {name: $name})",
                name=agent_name
            )
            
            # Save receipt node
            if receipt_id:
                tx.run(
                    "MERGE (r:Receipt {id: $id}) "
                    "SET r.action = $action, r.timestamp = $ts "
                    "WITH r "
                    "MATCH (a:Agent {name: $agent}) "
                    "MERGE (a)-[:AUTHORIZED_BY]->(r)",
                    id=receipt_id,
                    action=action or "TOOL_EXECUTION",
                    ts=str(time.time()),
                    agent=agent_name
                )
                
                agents_map[receipt_id] = agent_name
                
                # Link delegation
                if parent_id and parent_id in agents_map:
                    parent_agent = agents_map[parent_id]
                    tx.run(
                        "MATCH (p:Agent {name: $parent}), (c:Agent {name: $child}) "
                        "MERGE (p)-[:DELEGATES_TO]->(c)",
                        parent=parent_agent,
                        child=agent_name
                    )

            # Link project validated/optimized by agents
            if "Validation" in agent_name:
                tx.run(
                    "MATCH (p:Project {name: $project}), (a:Agent {name: $agent}) "
                    "MERGE (p)-[:VALIDATED_BY]->(a) "
                    "MERGE (a)-[:VALIDATED]->(p)",
                    project=project_name,
                    agent=agent_name
                )
            elif "Optimization" in agent_name:
                tx.run(
                    "MATCH (p:Project {name: $project}), (a:Agent {name: $agent}) "
                    "MERGE (p)-[:OPTIMIZED_BY]->(a)",
                    project=project_name,
                    agent=agent_name
                )
            elif "Planner" in agent_name:
                tx.run(
                    "MATCH (p:Project {name: $project}), (a:Agent {name: $agent}) "
                    "MERGE (p)-[:GENERATED_BY]->(a)",
                    project=project_name,
                    agent=agent_name
                )

    # 5. Ingest Project BOM Components
    components = package_data.get("components", [])
    for comp in components:
        comp_name = comp.get("component") or comp.get("name")
        if not comp_name:
            continue
            
        category = comp.get("category", "")
        cost = comp.get("final_cost") or comp.get("cost") or 0.0
        vendor_name = comp.get("optimal_vendor") or comp.get("vendor") or "Generic Vendor"
        
        # Merge component node
        tx.run(
            "MERGE (c:Component {name: $name}) "
            "SET c.category = $category, c.cost = $cost",
            name=comp_name,
            category=category,
            cost=cost
        )
        
        # Link Project USES Component
        tx.run(
            "MATCH (p:Project {name: $project}), (c:Component {name: $comp}) "
            "MERGE (p)-[:USES]->(c) "
            "MERGE (p)-[:HAS_BOM]->(c)",
            project=project_name,
            comp=comp_name
        )
        
        # Ingest Vendor Sells Component
        tx.run(
            "MATCH (c:Component {name: $comp}) "
            "MERGE (v:Vendor {name: $vendor}) "
            "MERGE (v)-[:SELLS]->(c) "
            "MERGE (c)-[:AVAILABLE_AT]->(v) "
            "WITH c, v "
            "MATCH (p:Project {name: $project}) "
            "MERGE (v)-[:SUPPLIES]->(p)",
            comp=comp_name,
            vendor=vendor_name,
            project=project_name
        )

        # 6. Ingest alternative components
        alternatives = comp.get("alternatives", [])
        for alt in alternatives:
            alt_name = alt.get("alternative") or alt.get("name")
            if not alt_name:
                continue
            alt_cost = alt.get("final_cost") or alt.get("cost") or 0.0
            tx.run(
                "MATCH (c:Component {name: $comp}) "
                "MERGE (alt:Component {name: $alt_name}) "
                "SET alt.cost = $alt_cost "
                "MERGE (c)-[:ALTERNATIVE_TO]->(alt)",
                comp=comp_name,
                alt_name=alt_name,
                alt_cost=alt_cost
            )

        # 7. Ingest default failure modes
        cat_lower = category.lower()
        fms = []
        if "controller" in cat_lower or "esp32" in comp_name.lower():
            fms = [
                {"name": "GPIO short-circuit", "severity": "High", "mitigation": "Install series resistors on I/O lines."},
                {"name": "Voltage spike on 3.3V line", "severity": "Critical", "mitigation": "Use stable voltage regulators."}
            ]
        elif "battery" in comp_name.lower() or "power" in cat_lower:
            fms = [
                {"name": "Thermal runaway", "severity": "Critical", "mitigation": "BMS temperature monitoring."}
            ]
        for fm in fms:
            tx.run(
                "MATCH (c:Component {name: $comp}) "
                "MERGE (f:FailureMode {id: $fm_id}) "
                "SET f.name = $name, f.severity = $severity, f.mitigation = $mitigation "
                "MERGE (c)-[:HAS_FAILURE_MODE]->(f)",
                comp=comp_name,
                fm_id=f"fm_{comp_name}_{fm['name']}".replace(" ", "_"),
                name=fm["name"],
                severity=fm["severity"],
                mitigation=fm["mitigation"]
            )

    # 8. Ingest Wiring & Pins
    wiring = package_data.get("wiring_diagram", {})
    if isinstance(wiring, dict):
        connections = wiring.get("connections") or wiring.get("wires") or []
        for conn in connections:
            from_comp = conn.get("from_component") or conn.get("source")
            to_comp = conn.get("to_component") or conn.get("target")
            from_pin = conn.get("from_pin") or conn.get("source_pin")
            to_pin = conn.get("to_pin") or conn.get("target_pin")
            protocol = conn.get("protocol") or "GPIO"
            
            if from_comp and to_comp:
                # Link components directly
                tx.run(
                    "MATCH (c1:Component {name: $from_comp}), (c2:Component {name: $to_comp}) "
                    "MERGE (c1)-[:CONNECTED_TO]->(c2)",
                    from_comp=from_comp,
                    to_comp=to_comp
                )
                
                # Ingest protocol
                tx.run(
                    "MERGE (proto:Protocol {name: $protocol}) "
                    "WITH proto "
                    "MATCH (c1:Component {name: $from_comp}), (c2:Component {name: $to_comp}) "
                    "MERGE (c1)-[:COMMUNICATES_VIA]->(proto) "
                    "MERGE (c2)-[:COMMUNICATES_VIA]->(proto)",
                    protocol=protocol,
                    from_comp=from_comp,
                    to_comp=to_comp
                )

                if from_pin and to_pin:
                    p1_id = f"pin_{from_comp}_{from_pin}".replace(" ", "_")
                    p2_id = f"pin_{to_comp}_{to_pin}".replace(" ", "_")
                    tx.run(
                        "MERGE (p1:Pin {id: $p1_id}) SET p1.name = $p1_name, p1.component = $from_comp "
                        "MERGE (p2:Pin {id: $p2_id}) SET p2.name = $p2_name, p2.component = $to_comp "
                        "MERGE (p1)-[:CONNECTED_TO]->(p2) "
                        "WITH p1, p2 "
                        "MATCH (c1:Component {name: $from_comp}), (c2:Component {name: $to_comp}) "
                        "MERGE (c1)-[:HAS_PIN]->(p1) "
                        "MERGE (c2)-[:HAS_PIN]->(p2)",
                        p1_id=p1_id,
                        p1_name=from_pin,
                        from_comp=from_comp,
                        p2_id=p2_id,
                        p2_name=to_pin,
                        to_comp=to_comp
                    )

    # 9. Ingest Power
    power_analysis = package_data.get("power_analysis", {})
    if isinstance(power_analysis, dict):
        battery_name = power_analysis.get("battery_component") or "LiPo Battery Pack"
        tx.run(
            "MERGE (b:Battery:Component {name: $name}) "
            "SET b.capacity = $capacity, b.voltage = $voltage",
            name=battery_name,
            capacity=power_analysis.get("battery_capacity", "2200mAh"),
            voltage=power_analysis.get("nominal_voltage", "7.4V")
        )
        tx.run(
            "MATCH (p:Project {name: $project}), (b:Component {name: $battery}) "
            "MERGE (p)-[:USES]->(b)",
            project=project_name,
            battery=battery_name
        )

        rails = power_analysis.get("voltage_rails") or power_analysis.get("rails") or []
        for rail in rails:
            rail_comps = rail.get("components") or []
            for rc in rail_comps:
                tx.run(
                    "MATCH (c:Component {name: $rc}), (b:Battery {name: $battery}) "
                    "MERGE (c)-[:POWERED_BY]->(b)",
                    rc=rc,
                    battery=battery_name
                )

    # 10. Ingest Research Papers & Contradictions
    papers = package_data.get("papers", [])
    for paper in papers:
        title = paper.get("title")
        if not title:
            continue
        url = paper.get("url") or paper.get("pdf_url") or "https://arxiv.org"
        
        tx.run(
            "MATCH (p:Project {name: $project}) "
            "MERGE (rp:ResearchPaper {title: $title}) "
            "SET rp.url = $url "
            "MERGE (p)-[:SUPPORTED_BY]->(rp) "
            "MERGE (rp)-[:SUPPORTS]->(p)",
            project=project_name,
            title=title,
            url=url
        )

    # Contradictions
    contradictions = package_data.get("contradictions", [])
    for con in contradictions:
        p1 = con.get("paper1") or con.get("paper1_title")
        p2 = con.get("paper2") or con.get("paper2_title")
        if p1 and p2:
            tx.run(
                "MERGE (rp1:ResearchPaper {title: $p1}) "
                "MERGE (rp2:ResearchPaper {title: $p2}) "
                "MERGE (rp1)-[:CONTRADICTS]->(rp2)",
                p1=p1,
                p2=p2
            )

    # 11. Ingest Contribution Logs (Contribution Graph)
    tx.run(
        "MATCH (u:User {email: $email}), (p:Project {name: $project}) "
        "MERGE (u)-[:MODIFIED {timestamp: $ts}]->(p) "
        "MERGE (u)-[:GENERATED {timestamp: $ts}]->(p)",
        email=user_email,
        project=project_name,
        ts=str(time.time())
    )
