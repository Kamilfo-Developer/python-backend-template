"""Redis config."""

from pydantic import Field, RedisDsn

from app.lib.config.base import BaseSettings


class RedisConfig(BaseSettings):
    """Redis config."""

    url: RedisDsn = Field(default=RedisDsn("redis://localhost:6379"))
