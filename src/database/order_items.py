# database/order_items.py
from .connection import OrderItems
from .connection import get_db_connection

# ============================== CRUD: Order Items =============================
def insertOrderItem(item: OrderItems) -> None:
  try:
    with get_db_connection() as conn:
      with conn.cursor() as cur:
        cur.execute(
          """
          INSERT INTO order_items (
            order_id, item_id, quantity, customizations
          ) VALUES (%s, %s, %s, %s)
          """,
          (
            item.order_id,
            item.item_id,
            item.quantity,
            item.customizations
          )
        )
        conn.commit()
  except Exception as e:
    print(f"Cannot insert order item, reason: {e}")
    raise