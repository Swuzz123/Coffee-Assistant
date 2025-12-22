# agent/tools.py
from datetime import datetime
from typing import List, Dict
from langchain.tools import tool

from src.utils.settings import mappings
from src.utils.helpers import QueryClassifier
from src.database.connection import Orders, OrderItems
from src.database.order_items import insertOrderItem
from src.database.orders import insertOrder, updateOrderStatus, getOrderStatus
from src.database.menu_items import getExactItem, getTopItemsFromSub, getTopItemsFromMain, getMenuItemsByTitle

# ================================ TOOLS USAGE =================================
@tool
def hand_customer_query(query: str) -> list[str]:
  """
  Search the menu to find drinks or food based on customer requests.
  Use this tool when customers ask about what's available, want recommendations,
  or ask about specific items.
  """
  qc = QueryClassifier(mappings)
  classification = qc.classify_query(query)
  
  if classification["type"] == "item":
    return getExactItem(classification["keyword"])

  elif classification["type"] == "sub_category":
    return getTopItemsFromSub(classification["keyword"])

  elif classification["type"] == "main_category":
    return getTopItemsFromMain(classification["keyword"])

  else:
    return ["Tôi chưa hiểu bạn muốn uống gì. Bạn có thể mô tả rõ hơn không?"]

# ------------------------------------------------------------------------------ 
@tool 
def place_order(customer_id: str, items: List[Dict]) -> str:
  """
  Place a new order after customer confirms all details.
  ONLY use this tool when the customer explicitly confirms the order.
  
  Args:
    customer_id: The customer's ID (provided in system context)
    items: List of items with details, e.g.:
        [
          {
            "item_name": "Cà phê sữa đá",
            "quantity": 2,
            "customizations": {
              "size": "L",
              "ice": "50%",
              "sugar": "70%",
              "milk_type": "oat milk"
            }
          }
        ]
    
  Returns:
    Confirmation message with order ID and total price
  """
  try:
    # Step 1: Validate and calculate total
    total_price = 0
    validated_items = []
    
    for item in items:
      item_name = item["item_name"]
      quantity = item.get("quantity", 1)
      customizations = item.get("customizations", {})
      
      menu_items = getMenuItemsByTitle(item_name)
      if not menu_items:
        return f"Dạ vâng quán mình không có món '{item_name}' này ạ. Bạn có thể order món khác không?"

      menu_item = menu_items[0]
      base_price = float(menu_item["price"])
      
      # Adjust price based on size
      size = customizations.get("size", "M")
      if size == "S":
        final_price = base_price - 10000
      elif size == "L":
        final_price = base_price + 10000
      else:
        final_price = base_price
        
      total_price += final_price * quantity
      
      validated_items.append({
        "item_id": menu_item["id"],
        "item_name": menu_item["title"],
        "quantity": quantity,
        "customizations": customizations,
        "price": final_price
      })
      
    # Step 2: Create order
    new_order = Orders(
      customer_id = customer_id,
      status = "pending",
      total_price = total_price,
      order_time = datetime.now()
    )
    order_id = insertOrder(new_order)
    
    # Step 3: Insert order items
    for v in validated_items:
      order_item = OrderItems(
        order_id=order_id,
        item_id=v["item_id"],
        quantity=v["quantity"],
        customizations=str(v["customizations"])
      )
      insertOrderItem(order_item)
      
    # Format confirmation
    items_summary = "\n".join([
      f" {v['item_name']} x{v['quantity']} - {v['price']:,.0f} VND"
      for v in validated_items
    ])
    
    return f"""Đơn hàng đã được đặt thành công!
              **Mã đơn hàng:** #{order_id}
              **Tổng tiền:** {total_price:,.0f} VND

              **Chi tiết:**
              {items_summary}

              Cảm ơn quý khách! Đơn hàng sẽ sớm được chuẩn bị."""
  except Exception as e:
    print(f"Error placing order: {e}")
    import traceback
    traceback.print_exc()
    return f"Có lỗi xảy ra khi đặt hàng: {str(e)}"

# ------------------------------------------------------------------------------ 
@tool
def get_order_status(order_id: int) -> str:
  """
  Check the status of an existing order.
  Use this when customer asks about their order status.
    
  Args:
    order_id: The order ID to check
  
  Returns:
    Order status information
  """
  order = getOrderStatus(order_id)
  if not order:
    return f"Không tìm thấy đơn hàng #{order_id}"
  
  status_map = {
      "pending": "Đang chờ xử lý",
      "preparing": "Đang chuẩn bị",
      "ready": "Đã sẵn sàng",
      "completed": "Đã hoàn thành",
      "cancelled": "Đã hủy"
    }
    
  status_vn = status_map.get(order["status"], order["status"])
  return f"""**Đơn hàng #{order['id']}**
               Trạng thái: {status_vn}
               Tổng tiền: {order['total_price']:,.0f} VND"""

# ------------------------------------------------------------------------------ 
@tool
def cancel_order(order_id: int) -> str:
  """
  Cancel an existing order.
  Only use this when customer explicitly requests to cancel.
  Cannot cancel orders that are completed or already cancelled.
    
  Args:
    order_id: The order ID to cancel
  
  Returns:
    Confirmation or error message
  """
  order = getOrderStatus(order_id)
  if not order:
    return f"Không tìm thấy đơn hàng #{order_id}"
  
  status = order["status"].lower()
  if status in ["completed", "cancelled"]:
    return f"Không thể hủy đơn hàng #{order_id} (Trạng thái: {status})"

  try:
    updateOrderStatus(order_id, "cancelled")
    return f"Đơn hàng #{order_id} đã được hủy thành công."
  except Exception as e:
    return f"Lỗi khi hủy đơn: {str(e)}"
  
# =============================== TOOLS PACKAGE ================================
tools = [hand_customer_query, place_order, get_order_status, cancel_order]
  

