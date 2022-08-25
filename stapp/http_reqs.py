import uuid

from fastapi import status

from clients import get_async_client
from config import URL_POST, URL_USER, URL_USERS
from utils import get_sort_by_created_on


async def get_users() -> list[dict]:
    async with get_async_client() as client:
        resp = await client.get(URL_USERS)
        if resp.status_code != status.HTTP_200_OK:
            return
        else:
            result = resp.json()
            return result


async def delete_users() -> list[dict]:
    async with get_async_client() as client:
        resp = await client.delete(URL_USERS)
        if resp.status_code != status.HTTP_200_OK:
            return
        else:
            result = resp.json()
            return result


async def get_user_names() -> list[str]:
    users = await get_users()
    sorted_users = sorted(users, key=get_sort_by_created_on())
    return [user['name'] for user in sorted_users]


async def get_user(name: str) -> list[dict]:
    url = f'{URL_USER}/{name}'
    async with get_async_client() as client:
        resp = await client.get(url)
        result = resp.json()
        return result


async def post_user(payload: dict) -> list[dict]:
    url = f'{URL_USER}'
    async with get_async_client() as client:
        resp = await client.post(url, json=payload)
        if resp.status_code != status.HTTP_201_CREATED:
            return
        else:
            result = resp.json()
            return result


async def patch_user(name: str, payload: dict) -> list[dict]:
    url = f'{URL_USER}/{name}'
    async with get_async_client() as client:
        resp = await client.patch(url, json=payload)
        if resp.status_code != status.HTTP_200_OK:
            return
        else:
            result = resp.json()
            return result


async def delete_user(name: str) -> list[dict]:
    url = f'{URL_USER}/{name}'
    params = {'id': name}
    async with get_async_client() as client:
        resp = await client.delete(url, params=params)
        if resp.status_code != status.HTTP_200_OK:
            return
        else:
            result = resp.json()
            return result


async def get_post(pid: uuid.UUID) -> list[dict]:
    url = f'{URL_POST}/{pid}'
    async with get_async_client() as client:
        resp = await client.get(url)
        if resp.status_code != status.HTTP_200_OK:
            return
        else:
            result = resp.json()
            return result


async def post_post(payload: dict, author_name: str) -> list[dict]:
    url = f'{URL_POST}'
    params = {'author_name': author_name}
    async with get_async_client() as client:
        resp = await client.post(url, json=payload, params=params)
        if resp.status_code != status.HTTP_201_CREATED:
            return
        else:
            result = resp.json()
            return result


async def patch_post(pid: uuid.UUID, payload: dict) -> list[dict]:
    url = f'{URL_POST}/{pid}'
    async with get_async_client() as client:
        resp = await client.patch(url, json=payload)
        if resp.status_code != status.HTTP_200_OK:
            return
        else:
            result = resp.json()
            return result


async def delete_post(pid: uuid.UUID) -> list[dict]:
    url = f'{URL_POST}/{pid}'
    params = {'id': pid}
    async with get_async_client() as client:
        resp = await client.delete(url, params=params)
        if resp.status_code != status.HTTP_200_OK:
            return
        else:
            result = resp.json()
            return result
