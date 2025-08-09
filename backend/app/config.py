from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "OCR-RAG API"
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_KEY: str
    
    # OpenAI
    OPENAI_API_KEY: str
    
    # Storage
    UPLOAD_DIR: str = "./data/uploads"
    PROCESSED_DIR: str = "./data/processed"
    CACHE_DIR: str = "./data/cache"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Processing
    OCR_BATCH_SIZE: int = 5
    MAX_WORKERS: int = 4
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    BACKEND_URL: str = Field(default="http://localhost:8000", description="Backend URL")
    FRONTEND_URL: str = Field(default="http://localhost:3000", description="Frontend URL")

    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

settings = Settings()

# Create directories if they don't exist
for dir_path in [settings.UPLOAD_DIR, settings.PROCESSED_DIR, settings.CACHE_DIR]:
    os.makedirs(dir_path, exist_ok=True)