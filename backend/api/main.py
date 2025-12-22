# backend/api/main.py
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import chat
from src.database.connection import get_db_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
  """Lifecylce event"""
  print("\n" + "="*60)
  print("MT Coffee Shop API Starting...")
  print("="*60)
  yield
  print("\n" + "="*60)
  print("MT Coffee Shop API Shutting down...")
  print("="*60)

# Create FastAPI app
app = FastAPI(
  title="MT Coffee Shop",
  description="API for MT Coffee Shop AI Agent",
  version="1.0.0",
  lifespan=lifespan
)

# CORS middleware (Allow frontend call API)
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
  
@app.get("/", tags=["Root"])
async def root():
  """API root endpoint"""
  return {
    "status": "healthy",
    "message": "MT Coffee Chatbot",
    "version": "1.0.0"
  }
  
@app.get("/health", tags=["Health"])
async def health_check():
  """Health check endpoint"""
  db_status = "operational"
  try:
    with get_db_connection() as conn:
      with conn.cursor() as cur:
        cur.execute("SELECT 1")
  except Exception:
    db_status = "down"
    
  return {
    "status": "healthy" if db_status == "operational" else "degraded",
    "timestamp": datetime.now().isoformat(),
    "service": {
      "api": "operational",
      "agent": "operational",
      "database": db_status
    }
  }