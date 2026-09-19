import pytest
import pytest_asyncio
from Backend.app.db.database import engine, init_db, close_db, get_session, async_session_maker
from Backend.app.db.models import Base
from sqlalchemy import text


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await close_db()


@pytest_asyncio.fixture
async def db_session():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest.fixture(autouse=True)
def clear_registry():
    from Backend.app.workflow.registry import registry
    from Backend.app.nodes import register_nodes
    registry._nodes.clear()
    registry._metadata.clear()
    register_nodes(registry)
    yield
    registry._nodes.clear()
    registry._metadata.clear()