# agent/order_agent.py
from typing import List, Literal

from .tools import tools
from .state import OrderState
from .prompt import SYSTEM_PROMPT, WELCOME_MSG
from src.utils.llm_manager import LLMOrchestrator

from langgraph.prebuilt import ToolNode
from langgraph.graph import START, END, StateGraph
from langchain_core.messages import SystemMessage, AIMessage

class OrderAgent:
  def __init__(self, tools: List = tools):
    self.tools = tools
    self.tool_node = ToolNode(tools)
    self.llm_orchestator = LLMOrchestrator()
    self.llm_with_tools = self.llm_orchestator.get_llm()
    self.graph = self._build_graph()
    
  # ============================== NODE FUNCTIONS ==============================
  def chat_node(self, state: OrderState) -> OrderState:
    customer_id = state.get("customer_id", "unknown")
    
    if state['messages']:
      system_msg = SystemMessage(
        content=SYSTEM_PROMPT.format(customer_id=customer_id)
      )
      msgs = [system_msg] + list(state['messages'])
      output = self.llm_with_tools.invoke(msgs)
      
    else:
      output = AIMessage(WELCOME_MSG)
      
    return {"messages": [output]}
  
  def should_continue(self, state: OrderState) -> Literal["tools", "end"]:
    last = state["messages"][-1]
    
    if hasattr(last, "tool_calls") and last.tool_calls:
      return "tools"
    else:
      return "end"
    
  # =============================== BUILD GRAPH ================================
  def _build_graph(self):
    builder = StateGraph(OrderState)
    
    builder.add_node("chatbot", self.chat_node)
    builder.add_node("tools", self.tool_node)
    
    builder.add_edge(START, "chatbot")
    builder.add_edge("tools", "chatbot")
    
    builder.add_conditional_edges(
      "chatbot",
      self.should_continue,
      {
        "tools": "tools",
        "end": END,
      },
    )
        
    agent = builder.compile()
    return agent
  
  def get_graph(self):
    return self.graph
    
    