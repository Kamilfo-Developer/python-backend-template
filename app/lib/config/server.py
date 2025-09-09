"""Server config."""

from pydantic import Field

from app.lib.config.base import BaseSettings


class ServerConfig(BaseSettings):
    """Server config."""

    host: str = Field(default="localhost")
    port: int = Field(default=8000)
