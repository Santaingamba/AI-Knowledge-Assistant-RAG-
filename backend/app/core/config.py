import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Knowledge Assistant"
    API_V1_STR: str = "/api/v1"
    
    # Legacy PostgreSQL credentials (kept for backward compatibility)
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "ai_knowledge"
    # New Neon Serverless PostgreSQL URL
    NEON_DATABASE_URL: str = ""
    # Alias for backward compatibility – will be overwritten by NEON_DATABASE_URL if set
    DATABASE_URL: str = ""
    
    JWT_SECRET: str = None  # Must be set via environment
    CORS_ALLOWED_ORIGINS: str = ""  # Comma‑separated list of allowed origins
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    GEMINI_API_KEY: str = ""
    
    # Storage configuration
    STORAGE_BACKEND: str = "local"  # Options: local, s3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = ""
    AWS_S3_BUCKET: str = ""
    
    UPLOAD_PATH: str = "storage/documents"
    CHROMA_PATH: str = "storage/chroma"
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RETRIEVAL: int = 5
    TEMPERATURE: float = 0.0
    
    # Gemini model configuration
    GEMINI_MODEL: str = "gemini-1.5-pro"  # Adjust as needed
    
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

# Validate required secrets on startup
if not settings.JWT_SECRET:
    raise RuntimeError("JWT_SECRET must be set in the environment for production use.")

if not settings.GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY must be set in the environment to use the Gemini integration.")

# Ensure a database URL is provided (prefer Neon)
if not settings.NEON_DATABASE_URL:
    raise RuntimeError("NEON_DATABASE_URL must be set in the environment to connect to the database.")


# Optional: Warn if S3 storage is selected but boto3 is not installed
if settings.STORAGE_BACKEND.lower() == "s3" and not __import__("importlib").util.find_spec("boto3"):
    raise RuntimeError("STORAGE_BACKEND is set to 's3' but boto3 is not installed. Install boto3 or switch to 'local'.")

# Ensure directories exist
os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
os.makedirs(settings.CHROMA_PATH, exist_ok=True)
