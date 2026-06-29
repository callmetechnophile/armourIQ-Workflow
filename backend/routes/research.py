from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from backend.schemas.research_schemas import ResearchRequest, ResearchResponse
from backend.agents.planner_agent import run_engineering_pipeline

router = APIRouter(prefix="/api")

class ChatRequest(BaseModel):
    message: str
    intent: str
    recommendation: str

@router.post("/research", response_model=ResearchResponse)
def execute_research(payload: ResearchRequest):
    try:
        if not payload.intent.strip():
            raise HTTPException(status_code=400, detail="Engineering intent cannot be empty")
            
        result = run_engineering_pipeline(payload.intent)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Engineering pipeline failed: {str(e)}")

@router.post("/chat")
def chat_advisor(payload: ChatRequest):
    try:
        msg_lower = payload.message.lower()
        
        # High-fidelity thematic replies based on project details
        if "battery" in msg_lower or "power" in msg_lower or "energy" in msg_lower:
            reply = f"For the '{payload.intent}', power stability is paramount. We recommend integrating a 12.8V LiFePO4 battery pack connected to a dedicated charge controller as suggested: '{payload.recommendation}'. This cushions voltage drops and avoids motor stalling."
        elif "sensor" in msg_lower or "control" in msg_lower:
            reply = f"If using microcontroller nodes (like ESP32/Arduino) for control, ensure they are isolated from inductive motor draws using optocouplers or dedicated buck converters to filter high frequency switching noise."
        elif "cost" in msg_lower or "price" in msg_lower or "alternative" in msg_lower:
            reply = "To optimize your budget, you can select standard silicon diodes for back-EMF protection rather than premium components, and utilize integrated PCB distribution boards to reduce manual terminal wiring costs."
        elif "fuse" in msg_lower or "safety" in msg_lower:
            reply = f"Fusing individual power rails is critical. I suggest using modular 10A-15A blade fuses on your main line: '{payload.recommendation}'. This prevents cascade failures if a single brushless motor or servo experiences a rotor lock."
        else:
            reply = f"Analyzing '{payload.intent}': Regarding the architecture recommendation: '{payload.recommendation}', ensure that all modular connections are securely locked and you have integrated transient voltage suppressors (TVS diodes) on the primary power bus."
            
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot query failed: {str(e)}")

