"""Application dependencies."""

from collections.abc import AsyncGenerator

import httpx
from dishka import AsyncContainer, Scope, make_async_container
from dishka.integrations.aiogram import AiogramProvider
from dishka.integrations.fastapi import FastapiProvider
from dishka.integrations.faststream import FastStreamProvider
from dishka.provider import provide
from haolib.configs.idempotency import IdempotencyConfig
from haolib.configs.redis import RedisConfig
from haolib.configs.sqlalchemy import SQLAlchemyConfig
from haolib.dependencies.idempotency import IdempotencyProvider
from haolib.dependencies.redis import RedisProvider
from haolib.dependencies.sqlalchemy import SQLAlchemyProvider

from app.config import AppConfig


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
    return make_async_container(SQLAlchemyProvider(), RedisProvider(), AppProvider(), IdempotencyProvider())
