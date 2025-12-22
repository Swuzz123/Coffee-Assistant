import os
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI

class LLMOrchestrator:
  def __init__(self):
    self.env = os.getenv("ENV", "dev")
    
  # ----------------------------------------------------------------------------  
  
  def _init_ollama_model(self):
    try:
      model = ChatOllama(
        model="qwen2.5:3b",
        base_url="http://localhost:11434",
        temperature=0.5
      )
      return model
    except Exception as e:
      raise RuntimeError(f"Cannot connect Ollama model: {e}")

  # ----------------------------------------------------------------------------
  def _init_gemini_model(self):
    API_KEY = os.getenv("GOOGLE_API_KEY")
    if not API_KEY:
      raise RuntimeError(f"GOOGLE_API_KEY is not set")
    
    try:
      model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=API_KEY
      )
      return model
    except Exception as e:
      raise RuntimeError(f"Cannot connect Gemini model: {e}")
    
  # ----------------------------------------------------------------------------
  def get_llm(self):
    if self.env == "dev":
      return self._init_ollama_model()
    
    if self.env == "prod":
      return self._init_gemini_model()
    
    raise ValueError("Invalid Environment Type")