"""Ping endpoint."""

from fastapi import APIRouter

from app.lib.schemas.common import OKSchema


ping_router = APIRouter(prefix="/ping", tags=["ping"])


@ping_router.get("/")
async def ping() -> OKSchema:
    """Ping."""
    return OKSchema()
