# database/menu_items.py
import pandas as pd
from typing import List, Dict
from .connection import get_db_connection

# ============================== CRUD: Menu Items ==============================
def insertItems(data_path: str):
  try:
    with get_db_connection() as conn:
      with conn.cursor() as cur:
        # Check data existed or not
        cur.execute("SELECT COUNT(*) FROM menu_items")
        if cur.fetchone()[0] > 0:
          print("Data already exists in menu_items. Skipping ingestion.")
          return
        
        # If data not existed -> ingest data into db
        df = pd.read_csv(data_path)
        for _, row in df.iterrows():
          cur.execute(
            """
            INSERT INTO menu_items (
              title, price, image_url, description, main_category, sub_category
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
              row["title"],
              row["price"], 
              row["image_url"],
              row["description"],
              row["main_category"],
              row["sub_category"]
            )
          )
      conn.commit()
    print("Insert values successfully!")
  except Exception as e:
    print(f"Cannot insert values, reason: {e}")
    
# ------------------------------------------------------------------------------
def fetchMenuItems():
  try:
    with get_db_connection() as conn:
      with conn.cursor() as cur:
        cur.execute(
          """
          SELECT
            id, title, price, image_url, description, main_category, sub_category
          FROM menu_items
          ORDER BY id
          """
        )
        rows = cur.fetchall()
        
    print("Fetch item records successfully!")
    return rows
  except Exception as e:
    print(f"Cannot read the values, reason: {e}")
    return []

# ------------------------------------------------------------------------------ 
def getExactItem(item_name):
  """Return exact information of an item by its name"""
  try:
    with get_db_connection() as conn:
      with conn.cursor() as cur:
        cur.execute(
          """
          SELECT
            title, price, description, image_url
          FROM menu_items
          WHERE title = %s
          """, (item_name,)
        )
        row = cur.fetchone()
        return list(row)
  except Exception as e:
    return [f"Error: {e}", 0, ""]

# ---------------------------------------------------------------------------- 
def getSubCategories(main_cat):
  """Return exact information of an item by its name"""
  try:
    with get_db_connection() as conn:
      with conn.cursor() as cur:
        cur.execute(
          """
          SELECT 
            DISTINCT sub_category
          FROM menu_items
          WHERE main_category = %s
          """, (main_cat,)
        )
        rows = cur.fetchall()
        return [r[0] for r in rows if r[0] is not None]
  except Exception as e:
    return [f"Error: {e}"]

# ------------------------------------------------------------------------------  
def getTopItemsFromMain(main_cat):
  """Recommend top 5 items from main category if it has no subcategories"""
  try:
    with get_db_connection() as conn:
      with conn.cursor() as cur:
        # Check if has subcategories
        cur.execute(
          """
          SELECT 
            COUNT(DISTINCT sub_category)
          FROM menu_items
          WHERE main_category = %s
          AND sub_category != 'NaN'
          """, (main_cat,)
        )
        count = cur.fetchone()[0]
        if count == 0:
          # No subcategories, return items directly
          cur.execute(
            """
            SELECT 
              title, price, description, image_url
            FROM menu_items
            WHERE main_category = %s
            ORDER BY RANDOM()
            LIMIT 5
            """, (main_cat,)
          )
          rows = cur.fetchall()
          rows = [list(r) for r in rows]
          return rows
        else:
          # Has subcategories, return them
          return getSubCategories(main_cat)
  except Exception as e:
    return [(f"Error: {e}", 0, "")]

# ------------------------------------------------------------------------------
def getTopItemsFromSub(sub_cat):
  """Recommend top 5 items from sub category"""
  try:
      with get_db_connection() as conn:
        with conn.cursor() as cur:
          cur.execute(
            """
            SELECT title, price, description, image_url
            FROM menu_items
            WHERE sub_category = %s
            ORDER BY RANDOM()
            LIMIT 5
            """, (sub_cat,)
          )
          rows = cur.fetchall()
          rows = [list(r) for r in rows]
          return rows
  except Exception as e:
    return [(f"Error: {e}", 0, "")]

# ------------------------------------------------------------------------------ 
def getMenuItemsByTitle(item_name: str) -> List[Dict]:
  try:
    with get_db_connection() as conn:
      with conn.cursor() as cur:
        cur.execute(
          """
          SELECT 
            id, title, price 
          FROM menu_items
          WHERE LOWER(title) = LOWER(%s)
          """, (item_name,)
        )
        rows = cur.fetchall()
        
        return [
          {
            "id": row[0],
            "title": row[1],
            "price": row[2]
          }
          for row in rows
        ]
  except Exception as e:
    print(f"Error fetching item by title: {e}")
    return []