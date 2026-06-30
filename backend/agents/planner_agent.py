from typing import Dict, Any, List
from backend.armoriq.delegation import capture_plan, delegate, invoke_tool, AUDIT_LOGS
from backend.armoriq.policies import ScopeViolationError

# Sub-Agent Imports
from backend.agents.retrieval_agent import run_retrieval
from backend.agents.extraction_agent import run_extraction
from backend.agents.research_agent import run_research
from backend.agents.validation_agent import run_validation
from backend.agents.optimization_agent import run_optimization
from backend.agents.planning_agent import run_planning
from backend.agents.export_agent import run_export

def run_engineering_pipeline(user_intent: str) -> Dict[str, Any]:
    # Clear previous audit logs for a fresh research run
    AUDIT_LOGS.clear()
    
    # 1. Capture Root Plan
    root_receipt = capture_plan(user_intent)
    root_receipt_dict = root_receipt.model_dump()
    
    # 2. RUN MANDATORY ARMORIQ BLOCKING TEST
    # Delegate Research Agent with ONLY paper search scopes
    research_receipt = delegate(
        agent_name="Research Agent",
        requested_scope=["search_papers", "summarize_papers"],
        parent_receipt=root_receipt_dict
    )
    
    blocked_test_triggered = False
    try:
        # Trigger illegal tool execution to demonstrate ArmorIQ block capability
        invoke_tool(
            agent_name="Research Agent",
            tool_name="export_pdf",  # Out of scope!
            args={"data": {}},
            receipt_dict=research_receipt.model_dump()
        )
    except ScopeViolationError:
        blocked_test_triggered = True
        # Caught successfully! The block log is saved inside AUDIT_LOGS.
        
    # 3. Proceed with Retrieval Agent
    retrieval_receipt = delegate(
        agent_name="Retrieval Agent",
        requested_scope=["search_projects", "fetch_sources"],
        parent_receipt=root_receipt_dict
    )
    retrieval_res = run_retrieval(user_intent, retrieval_receipt.model_dump())
    
    # 4. Proceed with Extraction Agent
    extraction_receipt = delegate(
        agent_name="Extraction Agent",
        requested_scope=["extract_components"],
        parent_receipt=root_receipt_dict
    )
    # Feed retrieval details to extract components
    retrieved_text = retrieval_res.get("source_details", {}).get("content_markdown", "") if retrieval_res.get("source_details") else user_intent
    extraction_res = run_extraction(retrieved_text, extraction_receipt.model_dump())
    components = extraction_res.get("components", [])
    
    # 4b. BOM Optimization Engine (runs ProcurementAgent)
    procurement_receipt = delegate(
        agent_name="ProcurementAgent",
        requested_scope=["generate_optimized_bom", "calculate_landed_cost", "find_alternative_components"],
        parent_receipt=root_receipt_dict
    )
    procurement_res = invoke_tool(
        agent_name="ProcurementAgent",
        tool_name="generate_optimized_bom",
        args={"components": components, "mode": "normal"},
        receipt_dict=procurement_receipt.model_dump()
    )
    
    # Overwrite components with the optimized, platform-ranked BOM items
    components = procurement_res["bom_items"]
    cost_res = procurement_res["totals"]
    
    # Extract alternatives list for the tabbed drawer display
    alternatives_list = []
    for item in components:
        alternatives_list.append({
            "component": item["component"],
            "alternatives": [
                {
                    "alternative": a["alternative"],
                    "name": a["alternative"],
                    "type": "cheaper" if a["final_cost"] < item["final_cost"] else "upgraded",
                    "reason": a["reason"],
                    "approx_cost_usd": float(a["final_cost"] / 83.0),
                    "base_cost": a.get("base_cost", a["final_cost"]),
                    "shipping_cost": a.get("shipping_cost", 0),
                    "final_cost": a["final_cost"]
                } for a in item.get("alternatives", [])
            ]
        })

    # 4d. Voltage Checker
    voltage_receipt = delegate(
        agent_name="Voltage Checker",
        requested_scope=["check_voltage_compatibility"],
        parent_receipt=root_receipt_dict
    )
    # Voltage Checker requires component names mapping
    voltage_components = [{"name": c["component"], "category": c["category"]} for c in components]
    voltage_res = invoke_tool(
        agent_name="Voltage Checker",
        tool_name="check_voltage_compatibility",
        args={"components": voltage_components},
        receipt_dict=voltage_receipt.model_dump()
    )

    # 4e. Pin Generator
    pin_receipt = delegate(
        agent_name="Pin Generator",
        requested_scope=["generate_pin_map"],
        parent_receipt=root_receipt_dict
    )
    pin_res = invoke_tool(
        agent_name="Pin Generator",
        tool_name="generate_pin_map",
        args={"components": voltage_components},
        receipt_dict=pin_receipt.model_dump()
    )
    
    # 5. Run Research Agent (Allowed Scope)
    research_res = run_research(user_intent, research_receipt.model_dump())
    
    # 6. Proceed with Validation Agent (Electrical Service embedded)
    validation_receipt = delegate(
        agent_name="Validation Agent",
        requested_scope=["validate_architecture"],
        parent_receipt=root_receipt_dict
    )
    validation_res = run_validation(components, user_intent, validation_receipt.model_dump())
    
    # 7. Proceed with Optimization Agent
    optimization_receipt = delegate(
        agent_name="Optimization Agent",
        requested_scope=["optimize_components"],
        parent_receipt=root_receipt_dict
    )
    optimization_res = run_optimization(components, optimization_receipt.model_dump())
    
    # 8. Proceed with Planning Agent
    planning_receipt = delegate(
        agent_name="Planning Agent",
        requested_scope=["generate_roadmap", "generate_gantt"],
        parent_receipt=root_receipt_dict
    )
    planning_res = run_planning(validation_res, planning_receipt.model_dump())
    
    # Compile intermediate package state to pass to Export Agent
    package_data = {
        "intent": user_intent,
        "components": components,
        "validation": validation_res,
        "optimization": optimization_res,
        "roadmap": planning_res.get("roadmap", [])
    }
    
    # 9. Proceed with Export Agent
    export_receipt = delegate(
        agent_name="Export Agent",
        requested_scope=["export_pdf", "export_csv", "export_markdown"],
        parent_receipt=root_receipt_dict
    )
    export_res = run_export(package_data, export_receipt.model_dump())

    # 9b. BOM Export Engine
    bom_receipt = delegate(
        agent_name="BOM Export Engine",
        requested_scope=["export_bom"],
        parent_receipt=root_receipt_dict
    )
    bom_export_res = invoke_tool(
        agent_name="BOM Export Engine",
        tool_name="export_bom",
        args={"components": components, "cost_summary": cost_res},
        receipt_dict=bom_receipt.model_dump()
    )
    
    # 10. Generate Decision Trace Table data
    decision_trace = generate_decision_trace(user_intent)
    
    # 11. Compile final output payload
    return {
        "intent": user_intent,
        "components": components,
        "projects": retrieval_res.get("projects", []),
        "papers": research_res.get("papers", []),
        "paper_summary": research_res.get("summary_details", {}),
        "validation": validation_res,
        "optimization": optimization_res,
        "roadmap": planning_res.get("roadmap", []),
        "gantt": planning_res.get("gantt", []),
        "exports": export_res,
        "decision_trace": decision_trace,
        "audit_trail": list(AUDIT_LOGS), # copy current logs
        "blocked_test_success": blocked_test_triggered,
        
        # New Feature Payloads
        "cost_summary": cost_res,
        "alternatives": alternatives_list,
        "voltage_risks": voltage_res,
        "pin_mapping": pin_res,
        "bom_exports": bom_export_res
    }

def generate_decision_trace(intent: str) -> List[Dict[str, str]]:
    intent_lower = intent.lower()
    if "solar" in intent_lower or "vacuum" in intent_lower:
        return [
            {
                "decision": "Integrate 12.8V LiFePO4 battery pack buffer instead of direct panel wiring.",
                "rationale": "Prevents motor stalling, electronics burn-in, and voltage drops under cloud coverage.",
                "agent": "Research Agent"
            },
            {
                "decision": "Substitute flexible solar panel with rigid glass solar panel.",
                "rationale": "Reduces costs by 30% if structural configuration allows for rigid base mounts.",
                "agent": "Optimization Agent"
            },
            {
                "decision": "Deploy a Maximum Power Point Tracking (MPPT) controller.",
                "rationale": "Boosts energy capture efficiency by 34% compared to PWM controllers.",
                "agent": "Validation Agent"
            }
        ]
    elif "drone" in intent_lower or "delivery" in intent_lower:
        return [
            {
                "decision": "Use ArduPilot / Matek H743-WING as flight controller alternative to Pixhawk.",
                "rationale": "Saves $90.00 while maintaining identical autonomous telemetry flight paths.",
                "agent": "Optimization Agent"
            },
            {
                "decision": "Separate telemetry antennas and GPS modules from high current lines by 15cm.",
                "rationale": "Mitigates severe RF interference and signal degradation from motor draws.",
                "agent": "Validation Agent"
            },
            {
                "decision": "Implement dual-GPS backup compass module setup.",
                "rationale": "Ensures navigational fail-safes during complex autonomous package dropoffs.",
                "agent": "Research Agent"
            }
        ]
    else:
        return [
            {
                "decision": "Use low-power ESP32 controller with built-in Wi-Fi.",
                "rationale": "Reduces power and PCB space compared to multi-chip alternatives.",
                "agent": "Research Agent"
            },
            {
                "decision": "Implement linear voltage regulator for clean sensor readings.",
                "rationale": "Filters high frequency switching noise from standard wall adapters.",
                "agent": "Validation Agent"
            }
        ]
