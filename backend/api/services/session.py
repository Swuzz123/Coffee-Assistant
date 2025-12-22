# backend/api/services/session.py
import uuid
from typing import Dict, Optional
from datetime import datetime, timedelta

class SessionManager:
  """
  Manage sessions for all conversations
  Purpose in there is for demo so just using in-memory dict 
  """
  def __init__(self, ttl_minutes: int = 60):
    self.sessions: Dict[str, Dict] = {}
    self.ttl = timedelta(minutes=ttl_minutes)
    
  # ----------------------------------------------------------------------------  
  def create_session(self, customer_id: Optional[str]) -> tuple[str, str]:
    """
    Create a new session 
    
    Returns:
      (session_id, customer_id)
    """
    session_id = str(uuid.uuid4())
    
    # Create new customer_id if not exist
    if not customer_id:
      customer_id = f"CUST_{str(uuid.uuid4().hex[:8].upper())}"
      
    self.sessions[session_id] = {
      "customer_id": customer_id,
      "created_at": datetime.now(),
      "last_activity": datetime.now()
    }
    
    print(f"Created a new session: {session_id} for customer: {customer_id}")
    return session_id, customer_id
  
  # ----------------------------------------------------------------------------
  def get_customer_id(self, session_id: str) -> Optional[str]:
    """Get customer_id from session_id"""
    session = self.sessions.get(session_id)
    if not session:
      return None
    
    session["last_activity"] = datetime.now()
    return session["customer_id"]
  
  # ----------------------------------------------------------------------------
  def is_valid_session(self, session_id: str) -> bool:
    """Check the session_id is valid or not"""
    session = self.sessions.get(session_id)
    if not session:
      return False
    
    # Check TTL (Time to live)
    elapsed = datetime.now() - session["last_activity"]
    if elapsed > self.ttl:
      print(f"Session {session_id} expired")
      del self.sessions[session_id]
      return False
    
    return True
  
  # ----------------------------------------------------------------------------
  def cleanup_expired(self):
    """Cleanup the expired sessions"""
    now = datetime.now()
    expired = [
      sid for sid, session in self.sessions.items()
      if now - session["last_activity"] > self.ttl
    ]
    
    for sid in expired:
      del self.sessions[sid]
    if expired:
      print(f"Clean up {len(expired)} expired sessions")