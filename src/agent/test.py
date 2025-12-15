# agent/test.py
from typing import Literal
from .tools import tools
from .state import OrderState
from .utils import initModelLLM, SYSTEM_PROMPT, WELCOME_MSG

from langgraph.prebuilt import ToolNode
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage, AIMessage

# ================== NODE FUNCTIONS ==================
tool_node = ToolNode(tools)
llm_with_tools = initModelLLM().bind_tools(tools)

def should_continue(state: OrderState) -> Literal["tools", "human", "end"]:  
  """Decide next step based on last message"""
  if state.get("finished", False):
    print("END (user quit)")
    return "end"
  
  last = state["messages"][-1]
    
  if hasattr(last, "tool_calls") and last.tool_calls:
    print(f"TOOLS ({len(last.tool_calls)} call(s))")
    return "tools"
  else:
    print("HUMAN")
    return "human"

def chat_node(state: OrderState) -> OrderState:  
  """Main chatbot node that processes messages and decides actions"""
  customer_id = state.get("customer_id", "unknown")
    
  if state["messages"]:
    # Add system prompt with customer_id
    system_msg = SystemMessage(content=SYSTEM_PROMPT.format(customer_id=customer_id))
    msgs = [system_msg] + list(state["messages"])
    
    print(f"Sending {len(state['messages'])} messages to LLM...")
    output = llm_with_tools.invoke(msgs)
    
    # Debug: Check if LLM wants to call tools
    if hasattr(output, "tool_calls") and output.tool_calls:
      print(f"LLM requested {len(output.tool_calls)} tool call(s):")
      for tc in output.tool_calls:
        print(f"      - {tc['name']}: {tc['args']}")
    else:
      print(f"LLM response: {output.content[:100]}...")
  else:
    output = AIMessage(content=WELCOME_MSG)
    print(f"Welcome message sent")
  
  return {"messages": [output]}

# ============================== BUILD GRAPH ==============================
def CoffeeAgent():
  builder = StateGraph(OrderState)

  builder.add_node("chatbot", chat_node)
  # builder.add_node("human", human_node)
  builder.add_node("tools", tool_node)

  builder.add_edge(START, "chatbot")
  builder.add_edge("tools", "chatbot")
  # builder.add_edge("human", "chatbot")

  builder.add_conditional_edges(
    "chatbot",
    should_continue,
    {
      "tools": "tools",
      # "human": "human",
      "end": END
    }
  )
  
  checkpointer = MemorySaver()

  chat_graph = builder.compile(checkpointer=checkpointer)
  return chat_graph