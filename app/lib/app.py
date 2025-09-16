"""Application builder."""

from collections.abc import Awaitable, Callable
from typing import Self

from dishka import AsyncContainer, Scope
from dishka.integrations.fastapi import setup_dishka as setup_dishka_fastapi
from dishka.integrations.faststream import setup_dishka as setup_dishka_faststream
from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from faststream.confluent import KafkaBroker
from uvicorn import Config, Server

from app.config import AppConfig
from app.lib.exceptions.handler import register_exception_handlers
from app.lib.middlewares.idempotency import (
    IdempotencyKeysStorage,
    idempotency_middleware,
)
from app.lib.observability.fastapi import setup_observability_for_fastapi


class AppBuilder:
    """App builder."""

    def __init__(self, container: AsyncContainer, app: FastAPI) -> None:
        """Initialize the app builder."""
        self._container = container
        self._app = app
        setup_dishka_fastapi(container, app)

    async def setup_faststream(self, broker: KafkaBroker) -> Self:
        """Setup faststream."""
        setup_dishka_faststream(self._container, broker=broker, finalize_container=False)

        return self

    async def setup_idempotency_middleware(self) -> Self:
        """Setup idempotency middleware."""

        @self._app.middleware("http")
        async def idempotency_middleware_for_app(
            request: Request,
            call_next: Callable[[Request], Awaitable[Response]],
        ) -> Response:
            """Idempotency middleware for the app."""
            async with self._container(scope=Scope.REQUEST) as nested_container:
                return await idempotency_middleware(
                    request,
                    call_next,
                    await nested_container.get(IdempotencyKeysStorage),
                )

        return self

    async def setup_observability(self) -> Self:
        """Setup observability."""
        setup_observability_for_fastapi(self._app, config=(await self._container.get(AppConfig)).observability)

        return self

    async def setup_exception_handlers(self, should_observe_exceptions: bool = True) -> Self:  # noqa: FBT001 FBT002
        """Setup exception handlers."""
        register_exception_handlers(self._app, should_observe_exceptions=should_observe_exceptions)

        return self

    async def setup_cors_middleware(self) -> Self:
        """Setup CORS middleware."""
        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        return self

    async def setup_router(self, router: APIRouter) -> Self:
        """Setup router."""
        self._app.include_router(router)
        return self

    async def get_app(self) -> FastAPI:
        """Build the app."""

        return self._app

    async def get_server(self) -> Server:
        """Get the server."""
        app_config = await self._container.get(AppConfig)

        config = Config(
            self._app,
            host=app_config.server.host,
            port=app_config.server.port,
        )

        return Server(config)
