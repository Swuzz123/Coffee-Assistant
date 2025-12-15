# database/order_items.py
from .connection import OrderItems
from .connection import get_db_connection

# ============================== CRUD: Order Items =============================
def initOrderItems():
  try:
    with get_db_connection() as conn:
      with conn.cursor() as cur:
        cur.execute(
          """
          CREATE TABLE IF NOT EXISTS order_items (
            id                SERIAL PRIMARY KEY,
            order_id          INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
            item_id           INTEGER NOT NULL REFERENCES menu_items(id) ON DELETE CASCADE,
            quantity          INTEGER NOT NULL DEFAULT 1,
            customizations    TEXT
          )
          """
        )
        conn.commit()
        print("Successfully create Order Items table!")
  except Exception as e:
    print(f"Cannot create Order Items table, reason: {e}")

# ------------------------------------------------------------------------------ 
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