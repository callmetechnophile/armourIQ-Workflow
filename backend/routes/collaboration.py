from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.services.collaboration_service import (
    create_team, invite_member, assign_role, add_comment,
    fetch_activity_logs, get_team_members, get_project_comments
)

router = APIRouter(prefix="/api/collaboration", tags=["collaboration"])

class TeamCreate(BaseModel):
    name: str

class MemberInvite(BaseModel):
    team_id: int
    user_id: str
    email: str
    role: str

class RoleAssign(BaseModel):
    role: str

class CommentAdd(BaseModel):
    project_id: str
    section: str
    author: str
    content: str

@router.post("/teams")
def api_create_team(payload: TeamCreate):
    try:
        return create_team(payload.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/members")
def api_invite_member(payload: MemberInvite):
    try:
        return invite_member(payload.team_id, payload.user_id, payload.email, payload.role)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/members/{member_id}/role")
def api_assign_role(member_id: int, payload: RoleAssign):
    try:
        success = assign_role(member_id, payload.role)
        if not success:
            raise HTTPException(status_code=404, detail="Member not found")
        return {"status": "SUCCESS"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/comments")
def api_add_comment(payload: CommentAdd):
    try:
        return add_comment(payload.project_id, payload.section, payload.author, payload.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/comments/{project_id}")
def api_get_comments(project_id: str):
    try:
        return get_project_comments(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/members/{team_id}")
def api_get_members(team_id: int):
    try:
        return get_team_members(team_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activity/{team_id}")
def api_fetch_activity(team_id: int):
    try:
        return fetch_activity_logs(team_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
