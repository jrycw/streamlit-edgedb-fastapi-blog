import httpx
import pytest
from fastapi import status

from tests.utils import _get_random_string


@pytest.mark.asyncio
class TestBasic:
    async def test_get_random_url(self, test_async_client: httpx.AsyncClient):
        response = await test_async_client.get(_get_random_string(10))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_home(self, test_async_client: httpx.AsyncClient):
        response = await test_async_client.get('/')
        expected = {'hello': 'world!'}
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected
