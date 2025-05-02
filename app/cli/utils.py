"""Utility commands."""

from asyncio import run

import click
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import AppConfig
from app.lib.models.base import AbstractModel
from app.lib.services.jwt import JWTService

from .cli import cli


@cli.group()
def utils() -> None:
    """Utility command group for database operations."""


async def _reset_db() -> None:
    """Reset the database by dropping all tables."""
    config = AppConfig.from_env()
    engine = create_async_engine(config.database.url)
    async with engine.begin() as conn:
        await conn.run_sync(AbstractModel.metadata.drop_all)


@utils.command()
@click.option("--i-am-completely-sure-that-i-want-to-do-this", is_flag=True)
def reset_db(i_am_completely_sure_that_i_want_to_do_this: bool) -> None:
    """Reset the database after user confirmation."""
    accepted = i_am_completely_sure_that_i_want_to_do_this
    if not accepted:
        confirmation = input("Are you sure you want to reset the database? [y/N] ")
        if confirmation.lower() != "y":
            return
        accepted = True

    if accepted:
        run(_reset_db())


@utils.group()
def jwt() -> None:
    """JWTService-related commands."""


@jwt.command("encode")
@click.option("--data", "-d", help="The data to encode into the JWTService.")
@click.option(
    "--exp",
    "-e",
    default=None,
    help="The expiration time in minutes. Defaults to None.",
)
@click.option("--with-key", is_flag=True, help="Encode JWTService with secret key.")
def encode_jwt(data: str, exp: int | None, with_key: bool) -> None:
    """Encode data into a JWTService."""
    config = AppConfig.from_env()
    jwt_mgr = JWTService(config.jwt.secret_key, config.jwt.algorithm)
    # We need this noqa because print here used as a part of the UI
    print(jwt_mgr.encode(data, exp, {"secret_key": config.security.secret_key} if with_key else None))  # noqa: T201


@jwt.command("decode")
@click.option("--token", "-t", help="The JWTService to decode.")
def decode_jwt(token: str) -> None:
    """Decode a JWTService."""
    config = AppConfig.from_env()
    jwt_mgr = JWTService(config.jwt.secret_key, config.jwt.algorithm)
    # We need this noqa because print here used as a part of the UI
    print(jwt_mgr.decode(token))  # noqa: T201
