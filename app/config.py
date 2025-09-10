"""Application config."""

from __future__ import annotations

from pydantic import Field

from app.lib.config.base import BaseConfig
from app.lib.config.idempotency import IdempotencyConfig
from app.lib.config.redis import RedisConfig
from app.lib.config.server import ServerConfig
from app.lib.config.sqlalchemy import SQLAlchemyConfig
from app.lib.observability.config import ObservabilityConfig


# MUST ALWAYS BE LAST
class AppConfig(BaseConfig):
    """Application config."""

    observability: ObservabilityConfig = Field(default_factory=ObservabilityConfig)
    database: SQLAlchemyConfig
    redis: RedisConfig = Field(default_factory=RedisConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    idempotency: IdempotencyConfig = Field(default_factory=IdempotencyConfig)
