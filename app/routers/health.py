"""Health check router."""

from fastapi import APIRouter

health_router = APIRouter()


@health_router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
