from typing import Dict, List

# Static map of allowed scopes (tools) per agent name
AGENT_SCOPES: Dict[str, List[str]] = {
    "Planner Agent": ["delegate"],
    "Retrieval Agent": ["search_projects", "fetch_sources"],
    "Extraction Agent": ["extract_components"],
    "Cost Engine": ["calculate_total_cost"],
    "Alternative Finder": ["find_alternatives"],
    "Voltage Checker": ["check_voltage_compatibility"],
    "Pin Generator": ["generate_pin_map"],
    "BOM Export Engine": ["export_bom"],
    "Research Agent": ["search_papers", "summarize_papers"],
    "Validation Agent": ["validate_architecture"],
    "Optimization Agent": ["optimize_components"],
    "Planning Agent": ["generate_roadmap", "generate_gantt"],
    "Export Agent": ["export_pdf", "export_csv", "export_markdown"]
}
