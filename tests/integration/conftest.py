"""Fixtures for the integration tests."""

import asyncio
from asyncio import AbstractEventLoop
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
import pytest_asyncio
from dishka import AsyncContainer, Scope, make_async_container
from fastapi import FastAPI
from faststream.confluent import KafkaBroker, TestKafkaBroker
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine

from app.dependencies import AppProvider
from app.lib.app import AppBuilder
from app.lib.dependencies.redis import RedisProvider
from app.lib.dependencies.sqlalchemy import SAProvider
from app.lib.models.base import AbstractModel
from app.routers.queues.router import get_broker
from app.routers.router import router
from app.version import __version__


class MockAppProvider(AppProvider):
    """Mock container."""


@pytest_asyncio.fixture
async def container() -> AsyncContainer:
    """Get container."""
    return make_async_container(SAProvider(), RedisProvider(), MockAppProvider())


@pytest.fixture
def event_loop() -> Generator[AbstractEventLoop, Any]:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture()
async def init_db(container: AsyncContainer) -> None:
    """Initialize database for testing."""
    async with (await container.get(AsyncEngine)).begin() as conn:
        await conn.run_sync(AbstractModel.metadata.drop_all)
        await conn.run_sync(AbstractModel.metadata.create_all)


@pytest_asyncio.fixture()
async def clean_redis(container: AsyncContainer) -> None:
    """Clean Redis for testing."""
    async with container(scope=Scope.REQUEST) as nested_container:
        await (await nested_container.get(Redis)).flushdb()


@pytest_asyncio.fixture()
async def app(container: AsyncContainer) -> AsyncGenerator[FastAPI]:
    """Create FastAPI app for testing without bot polling."""
    builder = AppBuilder(
        container,
        FastAPI(
            title="Python Backend Template",
            description="Python Backend Template.",
            version=__version__,
        ),
    )
    await builder.setup_faststream(get_broker())
    await builder.setup_idempotency_middleware()
    await builder.setup_exception_handlers(should_observe_exceptions=False)
    await builder.setup_cors_middleware()
    await builder.setup_router(router=router)
    app = await builder.get_app()

    yield app


@pytest_asyncio.fixture()
async def test_client(app: FastAPI) -> AsyncGenerator[AsyncClient]:
    """Create test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver", follow_redirects=True) as client:
        yield client


@pytest_asyncio.fixture()
async def test_broker() -> AsyncGenerator[KafkaBroker]:
    """Create Kafka client."""
    async with TestKafkaBroker(broker=get_broker()) as broker:
        yield broker
