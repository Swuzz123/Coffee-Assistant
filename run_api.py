import uvicorn
from datetime import datetime

if __name__ == "__main__":
  print("\n" + "="*60)
  print(f"Starting MT Coffee Shop API Server")
  print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
  print("="*60 + "\n")
  
  uvicorn.run(
    "backend.main:app",
    host="0.0.0.0",
    port=8000,
    reload=True,
    log_level="info"
  )