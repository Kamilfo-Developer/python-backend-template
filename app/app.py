"""Module containing main FastAPI application."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from app.core.config import AppConfig
from app.dependencies.providers import app_provider
from app.lib.exceptions.handler import register_exception_handlers
from app.middlewares.idempotent_request import IdempotentRequestMiddleware
from app.middlewares.request_id import RequestIdMiddleware
from app.routers.v1.router import v1_router


class App:
    """FastAPI application wrapper."""

    def __init__(self, config: AppConfig, app: FastAPI | None = None) -> None:
        """Initialize FastAPI application.

        Args:
            config: Application configuration.
            app: Optional existing FastAPI instance. A new one is created if None.

        """
        self.config = config
        self.fastapi_app = app or FastAPI(lifespan=self.lifespan)

        self._setup_routes()
        self._setup_exception_handlers()
        self._setup_middleware()

    def _setup_routes(self) -> None:
        """Setup API routes."""
        self.fastapi_app.include_router(v1_router)

    def _setup_exception_handlers(self) -> None:
        """Setup custom exception handlers."""
        register_exception_handlers(self.fastapi_app)

    def _setup_middleware(self) -> None:
        """Setup application middleware."""
        dishka_container = make_async_container(app_provider)

        self.fastapi_app.add_middleware(
            IdempotentRequestMiddleware,
            dependencies_getter=dishka_container.get,
        )
        self.fastapi_app.add_middleware(RequestIdMiddleware)
        setup_dishka(dishka_container, self.fastapi_app)

    @classmethod
    def from_env(cls) -> Self:
        """Create application from environment variables."""
        return cls(AppConfig.from_env())

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncGenerator[None, None]:
        """Application lifespan handler for startup and shutdown events."""
        try:
            yield
        finally:
            await app.state.dishka_container.close()


def app() -> FastAPI:
    """Return FastAPI application instance for Uvicorn server."""
    return App.from_env().fastapi_app
