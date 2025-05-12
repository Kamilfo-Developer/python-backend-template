"""Main v1 API router that aggregates all route modules."""

from fastapi import APIRouter

from app.routers.v1.example import example_router
from app.routers.v1.ping import ping_router


v1_router = APIRouter(prefix="/v1")

v1_router.include_router(ping_router)
v1_router.include_router(example_router)
