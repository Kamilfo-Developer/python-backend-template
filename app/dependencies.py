"""Application dependencies."""

from collections.abc import AsyncGenerator

import httpx
from dishka import AsyncContainer, Scope, make_async_container
from dishka.integrations.aiogram import AiogramProvider
from dishka.integrations.fastapi import FastapiProvider
from dishka.integrations.faststream import FastStreamProvider
from dishka.provider import provide
from redis.asyncio import Redis

from app.config import AppConfig
from app.lib.dependencies.idempotency import IdempotencyProvider
from app.lib.dependencies.redis import RedisProvider
from app.lib.dependencies.sqlalchemy import SAProvider
from app.lib.middlewares.idempotency import IdempotencyKeysStorage
from app.lib.services.encryption import EncryptionService


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
    async def client(self) -> AsyncGenerator[httpx.AsyncClient]:
        """Get client.

        Returns:
            AsyncGenerator[httpx.AsyncClient]: A new AsyncGenerator instance.

        """
        async with httpx.AsyncClient() as client:
            yield client

    @provide(scope=Scope.REQUEST)
    async def encryption_service(self, app_config: AppConfig) -> EncryptionService:
        """Get encryption service."""
        return EncryptionService(app_config.secrets.encryption_key.get_secret_value())

    @provide(scope=Scope.REQUEST)
    async def idempotency_keys_storage(self, redis: Redis, app_config: AppConfig) -> IdempotencyKeysStorage:
        """Get idempotency keys storage."""
        return IdempotencyKeysStorage(redis, app_config.idempotency.ttl)


def create_container() -> AsyncContainer:
    """Create a container."""
    return make_async_container(SAProvider(), RedisProvider(), AppProvider(), IdempotencyProvider())
