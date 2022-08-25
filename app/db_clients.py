import edgedb
from edgedb.asyncio_client import AsyncIOClient

async_db_client: AsyncIOClient = edgedb.create_async_client()


def get_async_db_client() -> AsyncIOClient:
    return async_db_client
