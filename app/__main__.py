"""Main entry point for the application."""

import asyncio

import uvloop
from fastapi import FastAPI

from app.dependencies import create_container
from app.lib.app import AppBuilder
from app.routers.queues.router import mq_router
from app.routers.router import router
from app.version import __version__


async def main() -> None:
    """Main entry point for the application."""
    container = create_container()
    builder = AppBuilder(
        container,
        FastAPI(
            title="Python Backend Template",
            description="Python Backend Template.",
            version=__version__,
        ),
    )

    await builder.setup_faststream(mq_router.broker)
    await builder.setup_idempotency_middleware()
    await builder.setup_exception_handlers()
    await builder.setup_cors_middleware()
    await builder.setup_router(router)
    await builder.setup_observability()

    server = await builder.get_server()
    await server.serve()


if __name__ == "__main__":
    uvloop.install()
    asyncio.run(main())
