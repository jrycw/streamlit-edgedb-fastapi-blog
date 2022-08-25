import edgedb
from edgedb.asyncio_client import AsyncIOClient

one_test_async_db_client: AsyncIOClient = edgedb.create_async_client('test01')


def get_test_async_db_client() -> AsyncIOClient:
    return one_test_async_db_client
