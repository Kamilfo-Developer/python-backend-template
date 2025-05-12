"""FastAPI application."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self

from dishka import AsyncContainer, Provider, make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import AppConfig
from app.lib.exceptions.handler import register_exception_handlers
from app.lib.middlewares.idempotent_request import IdempotentRequestMiddleware
from app.lib.middlewares.request_id import RequestIdMiddleware
from app.lib.utils.openapi import get_openapi
from app.routers.v1.router import v1_router


class FastAPIApp:
    """FastAPI application wrapper."""

    def __init__(
        self,
        config: AppConfig,
        app_providers: list[FastapiProvider | Provider],
        app: FastAPI | None = None,
    ) -> None:
        """Initialize FastAPI application.

        Args:
            config: Application configuration.
            app_providers: list of Dishka providers.
            app: Optional existing FastAPI instance. A new one is created if None.

        """
        self.config = config
        self.fastapi_app = app or FastAPI(lifespan=self.lifespan)
        dishka_container = make_async_container(*app_providers)

        self._setup_routes()
        self._setup_exception_handlers()
        self._setup_middleware(dishka_container=dishka_container)
        self.fastapi_app.openapi_schema = get_openapi(
            title=self.fastapi_app.title,
            description=self.fastapi_app.description,
            version=self.fastapi_app.version,
            routes=self.fastapi_app.routes,
            exclude_tags=["internal", "debug"] if self.config.general.production else [],
        )
        setup_dishka(dishka_container, self.fastapi_app)

    def _setup_routes(self) -> None:
        """Setup API routes."""
        self.fastapi_app.include_router(v1_router)

    def _setup_exception_handlers(self) -> None:
        """Setup custom exception handlers."""
        register_exception_handlers(self.fastapi_app)

    def _setup_middleware(self, dishka_container: AsyncContainer) -> None:
        """Setup application middleware."""

        self.fastapi_app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.general.origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.fastapi_app.add_middleware(
            IdempotentRequestMiddleware,
            dependencies_getter=dishka_container.get,
        )
        self.fastapi_app.add_middleware(RequestIdMiddleware)

    @classmethod
    def from_env(cls, app_providers: list[FastapiProvider | Provider]) -> Self:
        """Create application from environment variables."""
        return cls(AppConfig.from_env(), app_providers)

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncGenerator[None, None]:
        """Application lifespan handler for startup and shutdown events."""
        try:
            yield
        finally:
            await app.state.dishka_container.close()
            await app.state.dishka_container.close()
            await app.state.dishka_container.close()
