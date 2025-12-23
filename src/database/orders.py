# database/orders.py
from .connection import Orders
from .connection import get_db_connection

# ================================ CRUD: Order =================================
def insertOrder(orders: Orders) -> int:
  try:
    with get_db_connection() as conn:
      with conn.cursor() as cur:
        cur.execute(
          """
          INSERT INTO orders (
            customer_id, status, total_price, order_time
          ) VALUES (%s, %s, %s, %s)
          RETURNING id
          """,
          (
            orders.customer_id,
            orders.status,
            orders.total_price,
            orders.order_time
          )
        )
        order_id = cur.fetchone()[0]
        conn.commit()
        print(f"Insert order {order_id} successfully!")
        return order_id
  except Exception as e:
    print(f"Cannot insert order {id}, reason: {e}")
    raise

# ------------------------------------------------------------------------------  
def updateOrderStatus(order_id: int, new_status: str) -> None:
  try:
    with get_db_connection() as conn:
      with conn.cursor() as cur:
        cur.execute(
          """
          UPDATE order SET status = %s WHERE id = order_id
          """, (new_status, order_id)
        )
        conn.commit()
  except Exception as e:
    print(f"Cannot update order status, reason: {e}")
    raise

# ------------------------------------------------------------------------------ 
def getOrderStatus(order_id: int) -> dict | None:
  try:
    with get_db_connection() as conn:
      with conn.cursor() as cur:
        cur.execute(
          """
          SELECT
            id, status, total_price
          FROM order
          WHERE id = %s
          """, (order_id,)
        )
        row = cur.fetchone()
        if row:
          return {
            "id": row[0],
            "status": row[1],
            "total_price": row[2]
          }
        return None
  except Exception as e:
    print(f"Cannot get order status, reason: {e}")
    return None