import uvicorn
from datetime import datetime
from src.database.ingestion import run_ingestion

if __name__ == "__main__":
  print("Checking and ingesting data...")
  try:
    run_ingestion()
  except Exception as e:
    print(f"Ingestion failed, but starting server anyway: {e}")
  
  print("\n" + "="*60)
  print(f"Starting MT Coffee Shop API Server")
  print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
  print("="*60 + "\n")
  
  uvicorn.run(
    "api.main:app",
    host="0.0.0.0",
    port=8000,
    reload=True,
    log_level="info"
  )