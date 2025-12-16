# backend/models/chat.py
from datetime import datetime
from langchain_core.messages import HumanMessage
from fastapi import APIRouter, HTTPException, status

from src.agent.graph import create_agent
from backend.services.session import SessionManager
from backend.models.schemas import (
  ChatStartRequest,
  ChatStartResponse,
  ChatMessageRequest, 
  ChatMessageResponse,
  ChatHistoryResponse,
  ErrorResponse
)

# Initialize variables
router = APIRouter(prefix="/chat", tags=["chat"])
session_manager = SessionManager(ttl_minutes=60) 
agent = create_agent()

# ------------------------------------------------------------------------------
@router.post(
  "/start",
  response_model=ChatStartResponse,
  summary="Start a new conversation",
  description="""
  Create new session for conversation
  
  - If `customer_id` = null -> create new customer_id (annoymous customer)
  - If `customer_id` exists -> use the customer_id () (customer comeback)
  
  Return `session_id`
  """
)
async def start_chat(request: ChatStartRequest):
  """Endpoint to start a new conversation"""
  try:
    # Create session
    session_id, customer_id = session_manager.create_session(
      customer_id=request.customer_id
    )
    
    # Invoke agent with empty state to get welcome message
    state = {
      "messages": [],
      "customer_id": customer_id,
      "finished": False
    }
    config = {"configurable": {"thread_id": session_id}}
    result = agent.invoke(state, config)
    
    welcome_msg = result["messages"][-1].content
    
    return ChatStartResponse(
      session_id=session_id,
      customer_id=customer_id,
      message=welcome_msg,
      timestamp=datetime.now()
    )
    
  except Exception as e:
    print(f"Error in start_chat: {e}")
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Failed to start chat: {str(e)}"
    )
    
# ------------------------------------------------------------------------------
@router.post(
  "/message",
  response_model=ChatMessageResponse,
  summary="Send message to agent",
  description="""
  Send user's message to agent and receive response
  
  Agent will execute:
  - Load conversation history from thread_id (session_id)
  - Process new message
  - Call tools if needed
  - Return response
  """
)
async def send_messsage(request: ChatMessageRequest):
  """Endpoint to send message to agent"""
  try:
    # Validate session
    if not session_manager.is_valid_session(request.session_id):
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired session"
      )
      
    customer_id = session_manager.get_customer_id(request.session_id)
    
    # Create state with new message
    state = {
      "messages": [HumanMessage(content=request.message)],
      "customer_id": customer_id,
      "finished": False
    }
    config = {"configurable": {"thread_id": request.session_id}}  
    
    print(f"\n{'='*60}")
    print(f"Processing message for session: {request.session_id}")
    print(f"Customer: {customer_id}")
    print(f"Message: {request.message}")
    print(f"{'='*60}\n")
    
    result = agent.invoke(state, config)
    
    # Get last response
    last_message = result["messages"][-1]
    response_text = last_message.content
    
    # Extract tool calls info (for debugging)
    tool_calls_info = None
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
      tool_calls_info = [
        {
          "name": tc.get("name"),
          "args": tc.get("args")
        }
        for tc in last_message.tool_calls
      ]
      
    return ChatMessageResponse(
      session_id=request.session_id,
      message=response_text,
      timestamp=datetime.now(),
      tool_calls=tool_calls_info
    )
    
  except HTTPException:
    raise
  except Exception as e:
    print(f"Error in send_message: {e}")
    import traceback
    traceback.print_exc()
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Failed to process message: {str(e)}"
    )

# ------------------------------------------------------------------------------
@router.get(
  "/history/{session_id}",
  response_model=ChatHistoryResponse,
  summary="Get chat history",
  description="Get all chat history conversation of a session"
)
async def get_history(session_id: str):
  """Endpoint to get chat history"""
  try:
    # Validate session
    if not session_manager.is_valid_session(session_id):
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired session"
      )
      
    customer_id = session_manager.get_customer_id(session_id)
    
    # Get state from checkpointer
    config = {"configurable": {"thread_id": session_id}}
    state = agent.get_state(config)  
    
    # Format message
    messages = []
    for msg in state.values.get("messages", []):
      messages.append({
        "role": msg.__class__.__name__.replace("Message", "").lower(),
        "content": msg.content,
        "timestamp": getattr(msg, "timestamp", None)
      })
      
    return ChatHistoryResponse(
      session_id=session_id,
      customer_id=customer_id,
      messages=messages
    )
    
  except HTTPException:
    raise
  except Exception as e:
    print(f"Error in get_history: {e}")
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Failed to get history: {str(e)}"
    )
    
# ------------------------------------------------------------------------------
@router.delete(
  "/clear/{session_id}",
  response_model=ErrorResponse,
  summary="Clear expired session",
  description="Clear all expired session"
)
async def clear_session(session_id: str):
  pass