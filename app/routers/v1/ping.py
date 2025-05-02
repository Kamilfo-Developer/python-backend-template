"""Ping endpoint."""

from litestar import Router, get

from app.lib.schemas.common import OKSchema


@get("/", response_model=OKSchema)
async def ping() -> OKSchema:
    """Ping."""
    return OKSchema()


ping_router = Router("/ping", tags=["ping"], route_handlers=(ping,))
