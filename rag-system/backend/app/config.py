import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # GitHub
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    GITHUB_REPO_URL = os.getenv("GITHUB_REPO_URL", "")
    
    # Ollama
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
    
    # Chroma
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    
    # API
    API_PORT = int(os.getenv("API_PORT", 8000))
    
    # Embedding
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 100

config = Config()
