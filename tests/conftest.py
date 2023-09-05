import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from typing import AsyncGenerator
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from src.database import get_async_session
from src import metadata
from src.config import (TEST_DB_HOST, TEST_DB_PORT, TEST_DB_NAME, TEST_DB_USER, TEST_DB_PASS)

from src.main import app


# DATABASE
DATABASE_URL= f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASS}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"

async_engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
metadata.bind = async_engine


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with async_engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        
        
# SETUP
@pytest.fixture(scope='session')
def event_loop(request):
    """Создание экземпляра ивент лупа для каждого тестового случая"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

client = TestClient(app)

@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
