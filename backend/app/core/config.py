import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Knowledge Assistant"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "ai_knowledge"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_knowledge"
    
    JWT_SECRET: str = "supersecret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    GEMINI_API_KEY: str = ""
    
    UPLOAD_PATH: str = "storage/documents"
    CHROMA_PATH: str = "storage/chroma"
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RETRIEVAL: int = 5
    TEMPERATURE: float = 0.0
    
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
os.makedirs(settings.CHROMA_PATH, exist_ok=True)
