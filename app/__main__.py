"""Main entry point for the application."""

import asyncio

from app.app import create_app, create_server
from app.dependencies import AppConfig, create_container
from app.lib.observability.fastapi import setup_observability_for_fastapi


async def main() -> None:
    """Main entry point for the application."""
    container = create_container()
    app = await create_app(container)

    setup_observability_for_fastapi(app, config=(await container.get(AppConfig)).observability)

    server = await create_server(container, app)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
