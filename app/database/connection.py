import os

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

def _get_database_url() -> str:
    # Default SQLite file in the project root.
    # You can override with DATABASE_URL (e.g. Postgres later).
    return os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./earthquake.db")


DATABASE_URL = _get_database_url()

# Async engine (recommended with FastAPI async endpoints/background tasks).
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)


async def init_db() -> None:
    """Create tables (idempotent)."""
    # Import Base lazily to avoid circular imports.
    from app.database.session import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

