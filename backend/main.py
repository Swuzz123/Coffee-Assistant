from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from contextlib import asynccontextmanager

app = FastAPI(
  title="MT Coffee Shop",
  description="API for MT Coffee Shop AI Agent",
  version="1.0.0",
  # lifespan=lifespan
)

@app.get("/health", tags=["Health"])
async def health_check():
  """Health check endpoint"""
  return {
    "status": "health",
    "service": "coffee-chatbot-api",
    "version": "1.0.0"
  }
  
@app.get("/", tags=["Root"])
async def root():
  """API root endpoint"""
  return {
    "message": "MT Coffee Chatbot",
    "version": "1.0.0",
    "health": "/health"
  }
  
if __name__ == "__main__":
  import uvicorn
  uvicorn.run(
      "main:app",
      host="0.0.0.0",
      port=8000,
      reload=True,
      log_level="info"
  )