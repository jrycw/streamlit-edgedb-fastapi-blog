import asyncio

import httpx
import pytest
import pytest_asyncio
from app.db_clients import get_async_db_client
from app.main import api
from asgi_lifespan import LifespanManager
from edgedb.asyncio_client import AsyncIOClient
from faker import Faker

from tests.db_clients import one_test_async_db_client


@pytest_asyncio.fixture(scope='session')
async def test_async_db_client():
    yield one_test_async_db_client


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def test_async_client():
    def get_test_async_db_client() -> AsyncIOClient:
        return one_test_async_db_client
    api.dependency_overrides[get_async_db_client] = get_test_async_db_client
    async with LifespanManager(api):
        base_url = 'http://127.0.0.1'
        async with httpx.AsyncClient(app=api, base_url=base_url) as test_client:
            yield test_client


@pytest_asyncio.fixture(scope='session')
async def fker():
    yield Faker()
