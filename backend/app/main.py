from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import api_router
from app.db.sqlmodel_db import engine, Base
from app.middleware.error_handler import global_exception_handler
from app.utils.logger import setup_logger

logger = setup_logger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB (in production, use Alembic migrations instead of this)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Application startup complete")
    yield
    # Clean up DB
    await engine.dispose()
    logger.info("Application shutdown complete")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    # Parse comma‑separated origins from env var; fall back to common dev URLs
    allow_origins=[origin.strip() for origin in settings.CORS_ALLOWED_ORIGINS.split(',') if origin.strip()] or ["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handler
app.add_exception_handler(Exception, global_exception_handler)

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
