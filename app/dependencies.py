"""Application dependencies."""

from collections.abc import AsyncGenerator

import httpx
from dishka import AsyncContainer, Scope, make_async_container
from dishka.integrations.aiogram import AiogramProvider
from dishka.integrations.fastapi import FastapiProvider
from dishka.integrations.faststream import FastStreamProvider
from dishka.provider import provide

from app.config import AppConfig
from app.lib.config.idempotency import IdempotencyConfig
from app.lib.config.redis import RedisConfig
from app.lib.config.sqlalchemy import SQLAlchemyConfig
from app.lib.dependencies.idempotency import IdempotencyProvider
from app.lib.dependencies.redis import RedisProvider
from app.lib.dependencies.sqlalchemy import SAProvider


class AppProvider(FastapiProvider, AiogramProvider, FastStreamProvider):
    """Applicatoin provider."""

    @provide(scope=Scope.APP)
    def app_config(self) -> AppConfig:
        """Get app config.

        Returns:
            AppConfig: The application configuration.

        """
        return AppConfig.from_env()

    @provide(scope=Scope.APP)
    async def idempotency_config(self, app_config: AppConfig) -> IdempotencyConfig:
        """Get idempotency config."""
        return app_config.idempotency

    @provide(scope=Scope.APP)
    async def sqlalchemy_config(self, app_config: AppConfig) -> SQLAlchemyConfig:
        """Get sqlalchemy config."""
        return app_config.database

    @provide(scope=Scope.APP)
    async def redis_config(self, app_config: AppConfig) -> RedisConfig:
        """Get redis config."""
        return app_config.redis

    @provide(scope=Scope.APP)
    async def client(self) -> AsyncGenerator[httpx.AsyncClient]:
        """Get client.

        Returns:
            AsyncGenerator[httpx.AsyncClient]: A new AsyncGenerator instance.

        """
        async with httpx.AsyncClient() as client:
            yield client


def create_container() -> AsyncContainer:
    """Create a container."""
    return make_async_container(SAProvider(), RedisProvider(), AppProvider(), IdempotencyProvider())
