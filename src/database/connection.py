"""
Database connection and session management.
Supports SQLite (development) and PostgreSQL (production).

Uses SQLAlchemy 2.0+ async engine.
Docs: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config.settings import SETTINGS
from src.database.models import Base


# Create async engine based on DATABASE_URL
engine = create_async_engine(
    SETTINGS.DATABASE_URL,
    echo=SETTINGS.DATABASE_ECHO,
    pool_pre_ping=True,  # Verify connections are alive
)

# Session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """
    Create all tables. Used for development.
    In production, use Alembic migrations instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """Drop all tables. USE WITH CAUTION — development only."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for database sessions.

    Usage:
        async with get_session() as session:
            result = await session.execute(select(User))
    """
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.

    Usage in FastAPI:
        @router.get("/users")
        async def get_users(session: AsyncSession = Depends(get_db_session)):
            ...
    """
    async with get_session() as session:
        yield session
