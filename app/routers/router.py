"""Application routers."""

from fastapi import APIRouter

from app.routers.health import health_router
from app.routers.queues.router import mq_router

router = APIRouter()

router.include_router(mq_router)
router.include_router(health_router)
