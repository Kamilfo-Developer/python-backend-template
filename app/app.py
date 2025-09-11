"""Application."""

from collections.abc import Awaitable, Callable

from dishka import AsyncContainer, Scope
from dishka.integrations.fastapi import setup_dishka as setup_dishka_fastapi
from dishka.integrations.faststream import setup_dishka as setup_dishka_faststream
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import Config, Server

from app.config import AppConfig
from app.lib.exceptions.handler import register_exception_handlers
from app.lib.middlewares.idempotency import (
    IdempotencyKeysStorage,
    idempotency_middleware,
)
from app.routers.queues.router import mq_router
from app.routers.router import router
from app.version import __version__


async def create_app(
    container: AsyncContainer,
) -> FastAPI:
    """Create the FastAPI application."""

    setup_dishka_faststream(container, broker=mq_router.broker, finalize_container=False)

    app = FastAPI(
        title="Reel-o-Matic Workspace API",
        description="Reel-o-Matic Workspace API.",
        version=__version__,
    )

    setup_dishka_fastapi(container, app)

    @app.middleware("http")
    async def idempotency_middleware_for_app(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Idempotency middleware for the app."""
        async with container(scope=Scope.REQUEST) as nested_container:
            return await idempotency_middleware(
                request,
                call_next,
                await nested_container.get(IdempotencyKeysStorage),
            )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app, should_observe_exceptions=True)

    app.include_router(router)

    return app


async def create_server(container: AsyncContainer, app: FastAPI) -> Server:
    """Create the server."""
    app_config = await container.get(AppConfig)
    config = Config(
        app,
        host=app_config.server.host,
        port=app_config.server.port,
    )

    return Server(config)
