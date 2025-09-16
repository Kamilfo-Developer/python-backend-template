"""Application config."""

from __future__ import annotations

from haolib.configs.base import BaseConfig
from haolib.configs.idempotency import IdempotencyConfig
from haolib.configs.observability import ObservabilityConfig
from haolib.configs.redis import RedisConfig
from haolib.configs.server import ServerConfig
from haolib.configs.sqlalchemy import SQLAlchemyConfig
from pydantic import Field


# MUST ALWAYS BE LAST
class AppConfig(BaseConfig):
    """Application config."""

    observability: ObservabilityConfig = Field(default_factory=ObservabilityConfig)
    database: SQLAlchemyConfig
    redis: RedisConfig = Field(default_factory=RedisConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    idempotency: IdempotencyConfig = Field(default_factory=IdempotencyConfig)
