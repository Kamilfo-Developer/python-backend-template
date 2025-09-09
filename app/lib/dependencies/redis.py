"""Redis provider."""

from collections.abc import AsyncGenerator

from dishka import Provider, Scope, provide
from redis.asyncio import ConnectionPool, Redis

from app.config import AppConfig


class RedisProvider(Provider):
    """Redis provider."""

    @provide(scope=Scope.APP)
    def redis_pool(self, app_config: AppConfig) -> ConnectionPool:
        """Get redis pool.

        Args:
            app_config (AppConfig): The application configuration.

        Returns:
            ConnectionPool: The redis pool.

        """
        return ConnectionPool.from_url(str(app_config.redis.url))

    @provide(scope=Scope.REQUEST)
    async def redis(self, redis_pool: ConnectionPool) -> AsyncGenerator[Redis]:
        """Get redis.

        Args:
            redis_pool (ConnectionPool): The redis pool.

        Returns:
            Redis: The redis instance.

        """
        redis = Redis(connection_pool=redis_pool)
        try:
            yield redis
        finally:
            await redis.aclose()
