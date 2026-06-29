from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, List
from backend.auth import get_current_user
from backend.database import save_package, get_user_history

router = APIRouter(prefix="/api/packages", tags=["Packages"])

class SavePackageSchema(BaseModel):
    intent: str
    readiness_score: int
    risk_score: int
    optimization_score: int
    data: Dict[str, Any]

class PackageResponseSchema(BaseModel):
    id: int
    intent: str
    readiness_score: int
    risk_score: int
    optimization_score: int
    data: Dict[str, Any]
    timestamp: str

@router.post("/save", status_code=status.HTTP_201_CREATED)
async def save_user_package(
    payload: SavePackageSchema,
    user_id: str = Depends(get_current_user)
):
    try:
        save_package(
            user_id=user_id,
            intent=payload.intent,
            readiness=payload.readiness_score,
            risk=payload.risk_score,
            optimization=payload.optimization_score,
            data=payload.data
        )
        return {"status": "SUCCESS", "message": "Package saved successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save package: {str(e)}"
        )

@router.get("/history", response_model=List[PackageResponseSchema])
async def get_user_package_history(
    user_id: str = Depends(get_current_user)
):
    try:
        history = get_user_history(user_id=user_id)
        return history
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve history: {str(e)}"
        )
