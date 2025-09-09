"""Idempotency dependencies."""

from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from app.lib.middlewares.idempotency import IdempotencyKeysStorage


class IdempotencyProvider(Provider):
    """Idempotency provider."""

    @provide(scope=Scope.REQUEST)
    async def idempotency_keys_storage(self, redis: Redis, ttl: int) -> IdempotencyKeysStorage:
        """Get idempotency keys storage.

        Args:
            redis: Redis instance.
            ttl: Time to live for the idempotency key in milliseconds.

        Returns:
            IdempotencyKeysStorage: The idempotency keys storage.

        """
        return IdempotencyKeysStorage(redis, ttl)
