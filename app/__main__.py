"""Main entry point for the application."""

import asyncio

import uvloop
from fastapi import FastAPI
from haolib.app import AppBuilder
from haolib.configs.observability import ObservabilityConfig
from haolib.configs.server import ServerConfig

from app.dependencies import create_container
from app.routers.queues.router import mq_router
from app.routers.router import router
from app.version import __version__


async def main() -> None:
    """Main entry point for the application."""
    container = create_container()
    app = FastAPI(
        title="Python Backend Template",
        description="Python Backend Template.",
        version=__version__,
    )

    app.include_router(router)

    builder = AppBuilder(
        container,
        app,
    )

    await builder.setup_faststream(mq_router.broker)
    await builder.setup_idempotency_middleware()
    await builder.setup_exception_handlers()
    await builder.setup_cors_middleware()
    await builder.setup_observability(observability_config=await container.get(ObservabilityConfig))

    server = await builder.get_server(server_config=await container.get(ServerConfig))
    await server.serve()


if __name__ == "__main__":
    uvloop.install()
    asyncio.run(main())
