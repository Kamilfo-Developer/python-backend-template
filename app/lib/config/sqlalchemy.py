"""SQLAlchemy config."""

from app.lib.config.base import BaseSettings


class SQLAlchemyConfig(BaseSettings):
    """SQLAlchemy config."""

    url: str
