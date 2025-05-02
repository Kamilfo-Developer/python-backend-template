"""Module containing main Litestar application."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self

from dishka import make_async_container
from dishka.integrations.litestar import setup_dishka
from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import SwaggerRenderPlugin
from litestar.openapi.spec import Components, SecurityScheme
from litestar.plugins.problem_details import ProblemDetailsConfig, ProblemDetailsPlugin

from app.core.dependencies.providers import app_provider

from .core.config import AppConfig
from .lib.exceptions.handler import register_exception_handlers
from .lib.utils.sentry import configure_sentry
from .routers import router
from .routers.middlewares import IdempotentRequestMiddleware, RequestIdMiddleware
from .version import __version__


class LitestarApp:
    """Litestar application."""

    def __init__(self, config: AppConfig, app: Litestar | None = None) -> None:
        """Initialize Litestar application.

        Args:
            config (AppConfig): Application config.
            app (Litestar, optional): Litestar application. If set to None, a new
                application will be created. If set to an existing Litestar
                application, it will be used (but not instance configuration
                will be applied).

        """
        self.config = config
        self.litestar_app = app or Litestar(
            openapi_config=OpenAPIConfig(
                title="Application",
                description="Application API.",
                version=__version__,
                servers=[],
                render_plugins=[SwaggerRenderPlugin()],
                path="/docs",
                components=Components(security_schemes={"HTTPBearer": SecurityScheme("http", scheme="Bearer")}),
            ),
            middleware=[
                RequestIdMiddleware(),
                IdempotentRequestMiddleware(),
            ],
            cors_config=CORSConfig(
                allow_origins=self.config.general.origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            ),
            plugins=[
                ProblemDetailsPlugin(ProblemDetailsConfig(enable_for_all_http_exceptions=True)),
            ],
            lifespan=[self.lifespan],
        )
        # litestar main router
        self.litestar_app.register(router)
        # exception handler
        register_exception_handlers(self.litestar_app)
        # DI container
        dishka_container = make_async_container(app_provider)
        setup_dishka(dishka_container, self.litestar_app)

    @classmethod
    def from_env(cls) -> Self:
        """Create application from environment variables."""
        return cls(AppConfig.from_env())

    @asynccontextmanager
    async def lifespan(self, app: Litestar) -> AsyncGenerator[None, None]:
        """Lifespan."""
        configure_sentry(self.config.sentry.url)

        try:
            yield
        finally:
            await app.state.dishka_container.close()


def app() -> Litestar:
    """Return Litestar application.

    This function is used by Uvicorn to run the application.
    """
    return LitestarApp.from_env().litestar_app
