from typing import Dict, List

# Static map of allowed scopes (tools) per agent name
AGENT_SCOPES: Dict[str, List[str]] = {
    "Planner Agent": ["delegate", "generate_dependency_graph", "ask_connection_assistant"],
    "Retrieval Agent": ["search_projects", "fetch_sources"],
    "Extraction Agent": ["extract_components", "fetch_datasheets"],
    "Cost Engine": ["calculate_total_cost"],
    "Alternative Finder": ["find_alternatives"],
    "Voltage Checker": ["check_voltage_compatibility", "calculate_power_budget"],
    "Pin Generator": ["generate_pin_map", "generate_wiring_diagram"],
    "BOM Export Engine": ["export_bom"],
    "ProcurementAgent": ["generate_optimized_bom", "calculate_landed_cost", "find_alternative_components"],
    "Research Agent": ["search_papers", "summarize_papers", "rank_papers"],
    "Validation Agent": ["validate_architecture"],
    "Optimization Agent": ["optimize_components"],
    "Planning Agent": ["generate_roadmap", "generate_gantt"],
    "Export Agent": ["export_pdf", "export_csv", "export_markdown"]
}
