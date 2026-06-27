from fastapi import APIRouter, HTTPException
from backend.schemas.research_schemas import ResearchRequest, ResearchResponse
from backend.agents.planner_agent import run_engineering_pipeline

router = APIRouter(prefix="/api")

@router.post("/research", response_model=ResearchResponse)
def execute_research(payload: ResearchRequest):
    try:
        if not payload.intent.strip():
            raise HTTPException(status_code=400, detail="Engineering intent cannot be empty")
            
        result = run_engineering_pipeline(payload.intent)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Engineering pipeline failed: {str(e)}")
