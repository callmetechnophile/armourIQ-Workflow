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

import os
import json

@router.get("/receipts")
def list_receipts():
    try:
        from backend.armoriq.receipts import RECEIPTS_DIR
        receipts = []
        if os.path.exists(RECEIPTS_DIR):
            for filename in os.listdir(RECEIPTS_DIR):
                if filename.endswith(".json"):
                    filepath = os.path.join(RECEIPTS_DIR, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        try:
                            receipts.append(json.load(f))
                        except Exception:
                            pass
        # Sort receipts by timestamp descending
        receipts.sort(key=lambda r: float(r.get("timestamp", 0.0)), reverse=True)
        return receipts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ViolationRequest(BaseModel):
    agent: str
    tool: str

@router.post("/violations/simulate")
def simulate_violation(payload: ViolationRequest):
    try:
        from backend.armoriq.receipts import generate_receipt
        from backend.armoriq.delegation import invoke_tool
        from backend.armoriq.policies import ScopeViolationError
        
        # 1. Create a dummy receipt with agent's standard scope
        from backend.armoriq.scope_map import AGENT_SCOPES
        agent_scope = AGENT_SCOPES.get(payload.agent, [])
        
        dummy_receipt = generate_receipt(
            agent=payload.agent,
            scope=agent_scope,
            parent_receipt_id="dummy-parent-id"
        )
        
        # 2. Invoke tool
        invoke_tool(
            agent_name=payload.agent,
            tool_name=payload.tool,
            args={"data": {}},
            receipt_dict=dummy_receipt.model_dump()
        )
        
        return {"status": "SUCCESS", "message": "Invoked successfully (unexpected!)"}
    except ScopeViolationError as sve:
        # Find the latest blocked receipt hash
        from backend.armoriq.receipts import RECEIPTS_DIR
        blocked_hash = "N/A"
        latest_time = 0.0
        if os.path.exists(RECEIPTS_DIR):
            for filename in os.listdir(RECEIPTS_DIR):
                if filename.endswith(".json"):
                    filepath = os.path.join(RECEIPTS_DIR, filename)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            r_data = json.load(f)
                            if r_data.get("status") == "blocked" and r_data.get("agent") == payload.agent:
                                r_time = float(r_data.get("timestamp", 0.0))
                                if r_time > latest_time:
                                    latest_time = r_time
                                    blocked_hash = r_data.get("hash", "N/A")
                    except Exception:
                        pass
                        
        return {
            "status": "BLOCKED",
            "violated_scope": payload.tool,
            "requesting_agent": payload.agent,
            "expected_authority": agent_scope,
            "rejection_reason": f"Tool '{payload.tool}' is not in the delegated scope for '{payload.agent}'. Allowed scope: {agent_scope}.",
            "blocked_receipt_hash": blocked_hash
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

