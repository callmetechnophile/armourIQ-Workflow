from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ResearchRequest(BaseModel):
    intent: str

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
