"""Utility providers."""

from collections.abc import AsyncGenerator

from dishka import Provider, Scope, provide
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import AppConfig


class SAProvider(Provider):
    """SQLAlchemy provider."""

    @provide(scope=Scope.APP)
    async def db_engine(self, app_config: AppConfig) -> AsyncEngine:
        """Get db engine."""
        return create_async_engine(app_config.database.url)

    @provide(scope=Scope.APP)
    # Type ignore is needed because sessionmaker[AsyncSession] is not a subtype of sessionmaker[Session].
    async def db_session_maker(self, db_engine: AsyncEngine) -> sessionmaker[AsyncSession]:  # type: ignore[type-var]
        """Get db session maker.

        Args:
            db_engine (AsyncEngine): The db engine.

        Returns:
            sessionmaker[AsyncSession]: The db session maker.

        """
        # Type ignore is needed because for some reason SQLAlchemy doesn't understand the types properly.
        return sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)  # type: ignore[call-overload]

    @provide(scope=Scope.REQUEST)
    async def new_session(
        self,
        # Type ignore is needed because sessionmaker[AsyncSession] is not a subtype of sessionmaker[Session].
        db_session_maker: sessionmaker[AsyncSession],  # type: ignore[type-var]
    ) -> AsyncGenerator[AsyncSession]:
        """Get new database session.

        Args:
            db_session_maker (sessionmaker[AsyncSession]): The db session maker.

        Returns:
            AsyncSession: A new AsyncSessoin instance.

        """
        session = db_session_maker()
        try:
            yield session
        except SQLAlchemyError:
            await session.rollback()
            raise
        else:
            await session.commit()
        finally:
            await session.close()
