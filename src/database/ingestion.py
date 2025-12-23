# database/ingestion.py
from .menu_items import insertItems

def run_ingestion():
  
  csv_path = "/app/data/coffee_house_data.csv" 
  insertItems(csv_path)
    