from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ResearchRequest(BaseModel):
    intent: str
    target_days: Optional[int] = 22

class ExportResult(BaseModel):
    filename: str
    url: str
    status: str

class ResearchResponse(BaseModel):
    intent: str
    components: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]
    papers: List[Dict[str, Any]]
    paper_summary: Dict[str, Any]
    validation: Dict[str, Any]
    optimization: Dict[str, Any]
    roadmap: List[Dict[str, Any]]
    gantt: List[Dict[str, Any]]
    exports: Dict[str, ExportResult]
    decision_trace: List[Dict[str, str]]
    audit_trail: List[Dict[str, Any]]
    blocked_test_success: bool
    cost_summary: Optional[Dict[str, Any]] = None
    alternatives: Optional[List[Dict[str, Any]]] = None
    voltage_risks: Optional[List[Dict[str, Any]]] = None
    pin_mapping: Optional[List[Dict[str, Any]]] = None
    bom_exports: Optional[Dict[str, Any]] = None
    datasheets: Optional[List[Dict[str, Any]]] = None
    power_analysis: Optional[Dict[str, Any]] = None
    dependency_graph: Optional[Dict[str, Any]] = None
    wiring_diagram: Optional[Dict[str, Any]] = None
    contradictions: Optional[List[Dict[str, Any]]] = None
    thermal_analysis: Optional[List[Dict[str, Any]]] = None
    team_workspace: Optional[Dict[str, Any]] = None
    version_history: Optional[Dict[str, Any]] = None

