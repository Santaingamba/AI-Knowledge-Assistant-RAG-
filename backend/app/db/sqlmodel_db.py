from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.config import settings

# Async engine for Neon Serverless PostgreSQL
engine = create_engine(settings.NEON_DATABASE_URL, echo=(settings.ENVIRONMENT == "development"))

# Base metadata for migrations / table creation
Base = SQLModel
