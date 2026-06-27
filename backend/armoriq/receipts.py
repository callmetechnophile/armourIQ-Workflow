import hmac
import hashlib
import time
import uuid
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

SECRET_KEY = b"armoriq-cryptographic-secure-salt-2026"

class CryptographicReceipt(BaseModel):
    receipt_id: str
    timestamp: float
    agent: str
    scope: List[str]
    parent_receipt_id: Optional[str] = None
    input_hash: Optional[str] = None
    signature: str

def calculate_signature(receipt_id: str, timestamp: float, agent: str, scope: List[str], parent_receipt_id: Optional[str] = None, input_hash: Optional[str] = None) -> str:
    # Deterministic string representation of fields
    scope_str = ",".join(sorted(scope))
    parent_id_str = parent_receipt_id or ""
    hash_str = input_hash or ""
    
    payload = f"{receipt_id}|{timestamp}|{agent}|{scope_str}|{parent_id_str}|{hash_str}"
    
    mac = hmac.new(SECRET_KEY, payload.encode('utf-8'), hashlib.sha256)
    return mac.hexdigest()

def generate_receipt(agent: str, scope: List[str], parent_receipt_id: Optional[str] = None, input_data: Optional[Any] = None) -> CryptographicReceipt:
    receipt_id = str(uuid.uuid4())
    timestamp = time.time()
    
    # Calculate input hash if input_data is provided
    input_hash = None
    if input_data is not None:
        input_hash = hashlib.sha256(str(input_data).encode('utf-8')).hexdigest()
        
    sig = calculate_signature(receipt_id, timestamp, agent, scope, parent_receipt_id, input_hash)
    
    return CryptographicReceipt(
        receipt_id=receipt_id,
        timestamp=timestamp,
        agent=agent,
        scope=scope,
        parent_receipt_id=parent_receipt_id,
        input_hash=input_hash,
        signature=sig
    )

def verify_receipt(receipt: Dict[str, Any]) -> bool:
    try:
        receipt_id = receipt.get("receipt_id")
        timestamp = receipt.get("timestamp")
        agent = receipt.get("agent")
        scope = receipt.get("scope", [])
        parent_receipt_id = receipt.get("parent_receipt_id")
        input_hash = receipt.get("input_hash")
        signature = receipt.get("signature")
        
        if not receipt_id or not timestamp or not agent or signature is None:
            return False
            
        expected_sig = calculate_signature(receipt_id, timestamp, agent, scope, parent_receipt_id, input_hash)
        return hmac.compare_digest(expected_sig, signature)
    except Exception:
        return False
