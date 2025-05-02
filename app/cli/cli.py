"""Module with main CLI function."""

import click

from app.lib.utils.log import configure_logging


@click.group()
def cli() -> None:
    """Control interface for Status manager."""
    configure_logging()
