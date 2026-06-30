from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from backend.services.versioning_service import (
    get_project_versions, get_version_details,
    compare_versions, rollback_version, fork_project
)

from backend.armoriq.delegation import capture_plan, delegate, invoke_tool

router = APIRouter(prefix="/api/versioning", tags=["versioning"])

class ComparePayload(BaseModel):
    project_id: str
    v1: int
    v2: int

class RollbackPayload(BaseModel):
    project_id: str
    version_num: int

class ForkPayload(BaseModel):
    project_id: str
    version_num: int
    new_name: str
    user_id: str

@router.get("/versions/{project_id}")
def api_list_versions(project_id: str):
    try:
        return get_project_versions(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/versions/{project_id}/{version_num}")
def api_get_version(project_id: str, version_num: int):
    try:
        details = get_version_details(project_id, version_num)
        if not details:
            raise HTTPException(status_code=404, detail="Version not found")
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare")
def api_compare_versions(payload: ComparePayload):
    try:
        return compare_versions(payload.project_id, payload.v1, payload.v2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rollback")
def api_rollback_version(payload: RollbackPayload):
    try:
        root_receipt = capture_plan(f"Rollback project {payload.project_id} to version {payload.version_num}")
        version_receipt = delegate(
            agent_name="VersionAgent",
            requested_scope=["rollback_version"],
            parent_receipt=root_receipt.model_dump()
        )
        return invoke_tool(
            agent_name="VersionAgent",
            tool_name="rollback_version",
            args={
                "project_id": payload.project_id,
                "version_num": payload.version_num
            },
            receipt_dict=version_receipt.model_dump()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fork")
def api_fork_project(payload: ForkPayload):
    try:
        root_receipt = capture_plan(f"Fork project {payload.project_id} at version {payload.version_num}")
        version_receipt = delegate(
            agent_name="VersionAgent",
            requested_scope=["fork_project"],
            parent_receipt=root_receipt.model_dump()
        )
        return invoke_tool(
            agent_name="VersionAgent",
            tool_name="fork_project",
            args={
                "project_id": payload.project_id,
                "version_num": payload.version_num,
                "new_name": payload.new_name,
                "user_id": payload.user_id
            },
            receipt_dict=version_receipt.model_dump()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
