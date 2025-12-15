# agent/graph.py
from typing import Literal

from .tools import tools
from .state import OrderState
from .utils import initModelLLM, SYSTEM_PROMPT, WELCOME_MSG

from langgraph.prebuilt import ToolNode
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage, AIMessage

def create_agent():
  
  # ========================== INITIALIZE COMPONENTS ===========================
  tool_node = ToolNode(tools)
  llm_with_tools = initModelLLM().bind_tools(tools)
  
  # ============================== NODE FUNCTIONS ==============================
  def chat_node(state: OrderState) -> OrderState:
    """Main chatbot node that processes messages and decides actions"""
    customer_id = state.get("customer_id", "unknown")
    
    if state["messages"]:
      system_msg = SystemMessage(
        content=SYSTEM_PROMPT.format(customer_id=customer_id)
      )
      msgs = [system_msg] + list(state["messages"])
      output = llm_with_tools.invoke(msgs)
      
      if hasattr(output, "tool_calls") and output.tool_calls:
        print(f"   Tool calls: {len(output.tool_calls)}")
      
    else:
      output = AIMessage(content=WELCOME_MSG)
      
    return {"messages": [output]}
  
  def should_continue(state: OrderState) -> Literal["tools", "end"]:
    """Decide next step based on last message"""
    last = state["messages"][-1]
    
    if hasattr(last, "tool_calls") and last.tool_calls:
      print(f"   Tool calls: {len(last.tool_calls)}")
      return "tools"
    else:
      return "end"
  
  # =============================== BUILD GRAPH ================================  
  builder = StateGraph(OrderState)
  
  builder.add_node("chatbot", chat_node)
  builder.add_node("tools", tool_node)
  
  builder.add_edge(START, "chatbot")
  builder.add_edge("tools", "chatbot")
  
  builder.add_conditional_edges(
    "chatbot",
    should_continue,
    {
      "tools": "tools",
      "end": END
    },
  ) 
  
  checkpointer = MemorySaver()
  
  agent = builder.compile(checkpointer=checkpointer)
  
  return agent