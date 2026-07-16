"""
FastAPI application entrypoint.

Run locally with:
    uvicorn app.main:app --reload

Run via Docker:
    docker compose up --build
"""
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI

from app.api.v1.router import router as api_v1_router
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    """Handle application startup and shutdown events."""
    logger.info("Starting %s (env=%s, debug=%s)", settings.APP_NAME, settings.APP_ENV, settings.APP_DEBUG)
    yield
    logger.info("Shutting down %s", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.APP_DEBUG,
    lifespan=lifespan,
)

app.include_router(api_v1_router)
