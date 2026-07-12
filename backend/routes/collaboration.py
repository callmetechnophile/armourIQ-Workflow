from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.services.collaboration_service import (
    create_team, invite_member, assign_role, add_comment,
    fetch_activity_logs, get_team_members, get_project_comments
)
from backend.services.invitation_service import (
    create_team_invitation, get_team_invitation_by_token,
    accept_team_invitation, decline_team_invitation, get_team_by_id,
    get_team_by_uuid, create_and_invite_team
)

from backend.armoriq.delegation import capture_plan, delegate, invoke_tool

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
        root_receipt = capture_plan(f"Invite user {payload.user_id} to team {payload.team_id}")
        collab_receipt = delegate(
            agent_name="CollaborationAgent",
            requested_scope=["invite_member"],
            parent_receipt=root_receipt.model_dump()
        )
        return invoke_tool(
            agent_name="CollaborationAgent",
            tool_name="invite_member",
            args={
                "team_id": payload.team_id,
                "user_id": payload.user_id,
                "email": payload.email,
                "role": payload.role
            },
            receipt_dict=collab_receipt.model_dump()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/members/{member_id}/role")
def api_assign_role(member_id: int, payload: RoleAssign):
    try:
        root_receipt = capture_plan(f"Assign role {payload.role} to member {member_id}")
        collab_receipt = delegate(
            agent_name="CollaborationAgent",
            requested_scope=["assign_role"],
            parent_receipt=root_receipt.model_dump()
        )
        success = invoke_tool(
            agent_name="CollaborationAgent",
            tool_name="assign_role",
            args={
                "member_id": member_id,
                "role": payload.role
            },
            receipt_dict=collab_receipt.model_dump()
        )
        if not success:
            raise HTTPException(status_code=404, detail="Member not found")
        return {"status": "SUCCESS"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/comments")
def api_add_comment(payload: CommentAdd):
    try:
        root_receipt = capture_plan(f"Add comment to section {payload.section} of project {payload.project_id}")
        collab_receipt = delegate(
            agent_name="CollaborationAgent",
            requested_scope=["comment"],
            parent_receipt=root_receipt.model_dump()
        )
        return invoke_tool(
            agent_name="CollaborationAgent",
            tool_name="comment",
            args={
                "project_id": payload.project_id,
                "section": payload.section,
                "author": payload.author,
                "content": payload.content
            },
            receipt_dict=collab_receipt.model_dump()
        )
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

class TeamInviteRequest(BaseModel):
    email: str
    role: str

class AcceptInviteRequest(BaseModel):
    user_id: str

@router.post("/teams/{team_id}/invite")
def api_create_invite(team_id: int, payload: TeamInviteRequest):
    try:
        root_receipt = capture_plan(f"Create team invite for {payload.email} to team {team_id}")
        collab_receipt = delegate(
            agent_name="CollaborationAgent",
            requested_scope=["invite_member"],
            parent_receipt=root_receipt.model_dump()
        )
        return create_team_invitation(team_id, payload.email, payload.role)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/invitations/{token}")
def api_get_invite(token: str):
    inv = get_team_invitation_by_token(token)
    if not inv:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    team_info = get_team_by_id(inv["team_id"])
    members = get_team_members(inv["team_id"])
    
    return {
        "token": token,
        "team_name": team_info.get("name", "Team"),
        "team_uuid": team_info.get("uuid", ""),
        "description": "ARMOURLINE engineering collaboration workspace.",
        "owner": "Team Owner",
        "members": members,
        "projects": ["Hardware Rover", "Smart Solar Charger"],
        "created_on": team_info.get("created_at", ""),
        "status": inv["status"],
        "days_left": inv.get("days_left", 7),
        "expires_at": inv["expires_at"],
        "role": inv["role"],
        "email": inv["email"]
    }

@router.post("/invitations/{token}/accept")
def api_accept_invite(token: str, payload: AcceptInviteRequest):
    try:
        res = accept_team_invitation(token, payload.user_id)
        if res.get("status") == "error":
            raise HTTPException(status_code=400, detail=res.get("reason"))
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/invitations/{token}/decline")
def api_decline_invite(token: str):
    try:
        res = decline_team_invitation(token)
        if res.get("status") == "error":
            raise HTTPException(status_code=400, detail=res.get("reason"))
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teams/uuid/{uuid}")
def api_get_team_by_uuid(uuid: str):
    try:
        team_info = get_team_by_uuid(uuid)
        if not team_info:
            raise HTTPException(status_code=404, detail="Team not found")
        return team_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class CreateAndInviteRequest(BaseModel):
    team_name: str
    email: str
    role: str

@router.post("/teams/invite-collaborator")
def api_create_and_invite(payload: CreateAndInviteRequest):
    try:
        root_receipt = capture_plan(f"Create team {payload.team_name} and invite {payload.email}")
        collab_receipt = delegate(
            agent_name="CollaborationAgent",
            requested_scope=["invite_member"],
            parent_receipt=root_receipt.model_dump()
        )
        return create_and_invite_team(payload.team_name, payload.email, payload.role)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
