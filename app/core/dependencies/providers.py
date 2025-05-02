"""Application Dependency Injection providers."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, contextmanager

from aiochclient import ChClient
from dishka import Scope, provide
from dishka.integrations.litestar import LitestarProvider
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import AppConfig
from app.core.dependencies.constructors import (
    clickhouse_client,
    db_engine,
    db_session_autocommit,
    db_session_maker,
    redis_conn,
    redis_pool,
)
from app.lib.repositories.db_context import DBContext
from app.lib.repositories.sa_db_context import SADBContext


class AppProvider(LitestarProvider):
    """All the application dependencies provider."""

    # APP CONFIG PROVIDERS.
    @provide(scope=Scope.APP)
    def app_config(self) -> AppConfig:
        """Get application configuration.

        Returns:
            AppConfig: T    he application configuration.

        """
        return AppConfig.from_env()

    # DB PROVIDERS.
    @provide(scope=Scope.REQUEST)
    async def new_session(self, app_config: AppConfig) -> AsyncGenerator[AsyncSession, None]:
        """Get new database session.

        Args:
            app_config (AppConfig): The configuration of the app.

        Returns:
            AsyncSession: A new AsyncSessoin instance.

        """
        async with asynccontextmanager(self._get_new_session)(app_config) as session:
            yield session

    @provide(scope=Scope.REQUEST)
    async def new_db_context(self, app_config: AppConfig) -> AsyncGenerator[DBContext[AsyncSession], None]:
        """Get new database context.

        Args:
            app_config (AppConfig): The configuration of the app.

        Returns:
            DBContext: A new DBContext instance.

        """
        async with asynccontextmanager(self._get_new_session)(app_config) as session:
            yield SADBContext(session)

    async def _get_new_session(self, app_config: AppConfig) -> AsyncGenerator[AsyncSession, None]:
        with contextmanager(db_session_maker)(db_engine(app_config.database.url)) as session_maker:
            async with asynccontextmanager(db_session_autocommit)(session_maker) as session:
                yield session

    # CLICKHOUSE PROVIDERS.
    @provide(scope=Scope.REQUEST)
    async def new_clickhouse_client(self, app_config: AppConfig) -> AsyncGenerator[ChClient, None]:
        """Get new ClickHouse client.

        Args:
            app_config (AppConfig): The configuration of the app.

        Returns:
            ChClient: A new ChClient instance.

        """
        return clickhouse_client(app_config.clickhouse)

    # REDIS PROVIDERS.
    @provide(scope=Scope.REQUEST)
    async def new_redis(self, app_config: AppConfig) -> Redis:
        """Get new Redis instance.

        Args:
            app_config (AppConfig): The configuration of the app.

        Returns:
            Redis: The new instance of Redis.

        """
        return await anext(redis_conn(await anext(redis_pool(app_config.redis.url, decode_responses=True))))


app_provider = AppProvider()
