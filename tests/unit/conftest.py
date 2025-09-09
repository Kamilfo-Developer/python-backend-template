"""Mock container."""

from collections.abc import AsyncGenerator

import pytest_asyncio
from dishka import AsyncContainer, Scope, make_async_container

from app.dependencies import AppProvider


class MockAppProvider(AppProvider):
    """Mock container."""


@pytest_asyncio.fixture
async def container() -> AsyncGenerator[AsyncContainer]:
    """Get container."""
    container = make_async_container(MockAppProvider())
    async with container(scope=Scope.REQUEST) as nested_container:
        yield nested_container
