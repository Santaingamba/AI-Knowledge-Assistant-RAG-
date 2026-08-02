from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.utils.logger import setup_logger

logger = setup_logger("error_handler")

async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )
