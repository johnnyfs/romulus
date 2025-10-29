import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import AsyncSessionLocal


@pytest.fixture
async def db_session() -> AsyncSession:
    """Provides a database session for tests with automatic cleanup."""
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()  # Rollback any uncommitted changes after test


@pytest.fixture
def base_url() -> str:
    """Base URL for the running API server."""
    return "http://localhost:8000"
