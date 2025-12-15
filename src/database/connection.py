# database/connection.py
import os
import psycopg2
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
from contextlib import contextmanager
from pydantic import BaseModel, Field

load_dotenv()

# ============================= Connect to Database ============================
DSN = os.getenv("DATABASE_URL")

@contextmanager
def get_db_connection():
  conn = psycopg2.connect(DSN)
  try:
    yield conn
  finally:
    conn.close()

# ============================== Setup ORM types ===============================
class MenuItems(BaseModel):
  id:                  Optional[int] = None
  title:               str
  price:               float
  image_url:           str
  description:         str
  main_category:       str
  sub_category:        Optional[str] = None
  
class Orders(BaseModel):
  id:                  Optional[int] = None
  customer_id:         str
  status:              str
  total_price:         float
  order_time:          datetime = Field(default_factory=datetime.now)

class OrderItems(BaseModel):
  id:                  Optional[int] = None 
  order_id:            int
  item_id:             int
  quantity:            int
  customizations:      str
   
