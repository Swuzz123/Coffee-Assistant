from agent.test import CoffeeAgent

if __name__ == "__main__":
  print("=" * 60)
  print("MT COFFEE SHOP CHATBOT")
  print("=" * 60)
  print("Nhập 'q', 'quit', 'exit', hoặc 'tạm biệt' để thoát\n")
  
  state = {
    "messages": [],
    "customer_id": "CUST_001",
    "finished": False
  }
  
  agent = CoffeeAgent()
  
  try:
    agent.invoke(state)
  except KeyboardInterrupt:
    print("\n\nChatbot stopped by user")
  except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()