from typing import AsyncGenerator
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

# Single async engine for the entire application (Neon Serverless PostgreSQL)
engine = create_async_engine(
    settings.NEON_DATABASE_URL,
    echo=(settings.ENVIRONMENT == "development"),
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async SQLModel session.
    The session can be used with SQLModel ORM methods.
    """
    async with AsyncSession(engine) as session:
        yield session
