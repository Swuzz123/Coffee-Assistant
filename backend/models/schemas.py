# backend/models/schemas.py
import json
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional 

# ======================== INITIALIZE CONTEXT AND STATE ========================
class ChatStartRequest(BaseModel):
  """Request to start a new session"""
  customer_id: Optional[str] = None
  
  class Config:
    json_schema_extra = {
      "example": {
        "customer_id": "CUST_12345"
      }
    }
  
class ChatStartResponse(BaseModel):
  """Response to return session_id and welcome message"""
  session_id:   str
  customer_id:  str
  message:      str
  timestamp:    datetime

# ================= INITIALIZE REQUEST AND RESPONSE FROM USER ==================
class ChatMessageRequest(BaseModel):
  """Request to send message from user"""
  session_id:   str = Field(..., description="Session ID recieved from /chat/start")
  message:      str = Field(..., min_length=1, description="Message Content")
  
  class Config:
    json_schema_extra = {
      "example": {
        "session_id": "550e8400-e29b-41d4-a716-446655440000",
        "message": "Cho tôi xem menu cà phê"
      }
    }

class ChatMessageResponse(BaseModel): 
  """Response to return an answer from agent"""
  session_id:   str
  message:      str
  timestamp:    datetime
  tool_calls:   Optional[List[Dict[str, Any]]] = None 
  
class ChatHistoryResponse(BaseModel):
  """Response to return chat history"""
  session_id:   str
  customer_id:  str
  message:      List[Dict[str, Any]]
  
class ErrorResponse(BaseModel):
  """Reponse when having an error"""
  error:        str
  detail:       Optional[str] = None