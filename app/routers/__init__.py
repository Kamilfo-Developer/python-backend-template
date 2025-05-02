"""Module containing all routes."""

from litestar import Router

from app.routers.v1.router import v1_router

router = Router("/api", route_handlers=[v1_router])
