"""Application dependencies constructors."""

from collections.abc import AsyncGenerator, Generator
from typing import Any

from aiochclient import ChClient
from aiohttp import ClientSession
from redis.asyncio import ConnectionPool, Redis
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import ClickHouseConfig


def db_engine(database_url: str) -> AsyncEngine:
    """Create an asynchronous database engine.

    Args:
        database_url (str): The database URL for connecting to the database.

    Returns:
        AsyncEngine: An asynchronous engine instance configured with the specified database URL.

    """
    return create_async_engine(database_url, isolation_level="SERIALIZABLE")


def db_session_maker(
    engine: AsyncEngine | str,
) -> Generator[sessionmaker[Any], None, None]:
    """Create a session maker for database sessions.

    Args:
        engine (AsyncEngine | str): The database engine or a string URL to create the engine.

    Yields:
        sessionmaker[Any]: A sessionmaker instance for creating database sessions.

    """
    engine = engine if isinstance(engine, AsyncEngine) else db_engine(engine)
    maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)  # type: ignore[call-overload]
    yield maker
    maker.close_all()


async def db_session(maker: sessionmaker[Any]) -> AsyncGenerator[AsyncSession, None]:
    """Create an asynchronous database session.

    Args:
        maker (sessionmaker[Any]): The sessionmaker instance used to create the session.

    Yields:
        AsyncSession: An asynchronous session for database operations.

    Raises:
        SQLAlchemyError: If an error occurs during the session, the transaction is rolled back.

    """
    session = maker()
    try:
        yield session
    except SQLAlchemyError:
        await session.rollback()
        raise
    finally:
        await session.close()


async def db_session_autocommit(
    maker: sessionmaker[Any],
) -> AsyncGenerator[AsyncSession, None]:
    """Create an asynchronous database session with automatic commit on successful execution.

    Args:
        maker (sessionmaker[Any]): The sessionmaker instance used to create the session.

    Yields:
        AsyncSession: An asynchronous session for database operations.

    Raises:
        SQLAlchemyError: If an error occurs during the session, the transaction is rolled back.

    """
    session = maker()
    try:
        yield session
    except SQLAlchemyError:
        await session.rollback()
        raise
    else:
        await session.commit()
    finally:
        await session.close()


async def redis_pool(redis_url: str, **kwargs: Any) -> AsyncGenerator[ConnectionPool, None]:
    """Create a Redis connection pool.

    Args:
        redis_url (str): The URL for connecting to the Redis server.
        kwargs (Any): kwargs to pass to ConnectionPool.from_url()


    Yields:
        ConnectionPool: A connection pool for Redis connections.

    Note:
        The connection pool must be explicitly disconnected to release resources.

    """
    pool = ConnectionPool.from_url(redis_url, **kwargs)
    try:
        yield pool
    finally:
        await pool.disconnect()


async def redis_conn(pool: ConnectionPool) -> AsyncGenerator[Redis, None]:
    """Create a Redis connection from the connection pool.

    Args:
        pool (ConnectionPool): The connection pool to use for creating the Redis connection.

    Yields:
        Redis: A Redis connection instance.

    Finally:
        The connection is closed to release resources.

    """
    conn = Redis(connection_pool=pool)
    try:
        yield conn
    finally:
        await conn.close()


async def clickhouse_client(config: ClickHouseConfig) -> AsyncGenerator[ChClient, None]:
    """Get a ClickHouse client.

    Args:redis_conn(await anext(redis_pool(app_config.redis.url)))
        config (ClickHouseConfig): The configuration for connecting to the ClickHouse server.

    Yields:
        ChClient: A ClickHouse client instance for executing queries.

    """
    async with ClientSession() as session:
        yield ChClient(
            session,
            url=config.url,
            user=config.username,
            password=config.password,
            database=config.database,
        )
