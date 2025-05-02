"""Application V1 router."""

from litestar import Router

v1_router = Router("/v1", tags=["v1"], route_handlers=[])
