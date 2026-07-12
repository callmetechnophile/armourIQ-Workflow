from typing import Dict, Any, List
from backend.armoriq.receipts import verify_receipt
from backend.armoriq.scope_map import AGENT_SCOPES

class ScopeViolationError(Exception):
    """Raised when an agent attempts to invoke a tool outside of its authorized scope."""
    def __init__(self, agent: str, tool: str, allowed_scope: List[str], details: str = ""):
        self.agent = agent
        self.tool = tool
        self.allowed_scope = allowed_scope
        self.details = details
        super().__init__(f"Scope violation: Agent '{agent}' tried to execute '{tool}'. Allowed scope: {allowed_scope}. {details}")

def validate_tool_invocation(agent_name: str, tool_name: str, receipt_dict: Dict[str, Any]) -> bool:
    import os
    if os.environ.get("DISABLE_ARMORIQ") == "true":
        return True
        
    # 1. Cryptographic check - Verify signature of receipt
    if not verify_receipt(receipt_dict):
        raise ScopeViolationError(
            agent=agent_name,
            tool=tool_name,
            allowed_scope=[],
            details="Cryptographic verification failed: Invalid receipt signature or tampered data."
        )
    
    # 2. Extract scope from receipt
    allowed_scope = receipt_dict.get("scope", [])
    receipt_agent = receipt_dict.get("agent")
    
    # 3. Verify agent matches
    if receipt_agent != agent_name:
        raise ScopeViolationError(
            agent=agent_name,
            tool=tool_name,
            allowed_scope=allowed_scope,
            details=f"Receipt was issued for agent '{receipt_agent}', but invoked by '{agent_name}'."
        )
    
    # 4. Check if the tool is in the delegation receipt's scope
    if tool_name not in allowed_scope:
        raise ScopeViolationError(
            agent=agent_name,
            tool=tool_name,
            allowed_scope=allowed_scope,
            details=f"Tool '{tool_name}' is not in the delegated scope."
        )
        
    # 5. Check if the tool is in the static maximum boundaries for safety
    max_scopes = AGENT_SCOPES.get(agent_name, [])
    if tool_name not in max_scopes:
        raise ScopeViolationError(
            agent=agent_name,
            tool=tool_name,
            allowed_scope=allowed_scope,
            details=f"Tool '{tool_name}' exceeds the maximum structural boundaries for agent '{agent_name}'."
        )
        
    return True
