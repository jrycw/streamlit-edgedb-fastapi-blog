import json

import httpx
import pytest
import pytest_asyncio
from edgedb.asyncio_client import AsyncIOClient
from faker import Faker
from fastapi import status

from tests.utils import (
    _get_content,
    _get_email,
    _get_name,
    _get_random_string,
    _get_title,
    _get_uuid4_str,
    _is_reasonable_updatetime,
    _isinstance_uuid4,
    gen_post_data,
    gen_user_data,
)


@pytest_asyncio.fixture(scope='session')
async def init_user_n() -> int:
    yield 3


@pytest_asyncio.fixture(scope='session')
async def init_post_n() -> int:
    yield 3


@pytest_asyncio.fixture(scope='session')
async def valid_user_data_n() -> int:
    yield 3


@pytest_asyncio.fixture(scope='session')
async def valid_post_data_n() -> int:
    yield 3

# fixtures


@pytest_asyncio.fixture(scope='session')
async def _init_user_data(fker: Faker, init_user_n: int) -> list[dict]:
    yield gen_user_data(fker, n=init_user_n)


@pytest_asyncio.fixture(scope='session')
async def _init_post_data(fker: Faker, init_post_n: int) -> list[dict]:
    yield gen_post_data(fker, n=init_post_n)


@pytest_asyncio.fixture(scope='session')
async def valid_user_data(fker: Faker, valid_user_data_n: int) -> list[dict]:
    yield gen_user_data(fker, n=valid_user_data_n)


@pytest_asyncio.fixture(scope='session')
async def invalid_user_data(fker: Faker) -> list[dict]:
    user_data = gen_user_data(fker, n=6)
    del user_data[0]['email']
    del user_data[1]['name']
    user_data[2]['name'] = ''
    user_data[3]['name'] = _get_random_string(101)
    user_data[4]['email'] = 'this-email-contains_no-mouse.com'
    user_data[5]['email'] = 'fafiahhfia_@^%!%&!3.com'

    yield user_data


@pytest_asyncio.fixture(scope='session')
async def valid_post_data(fker: Faker, valid_post_data_n: int) -> list[dict]:
    yield gen_post_data(fker, n=valid_post_data_n)


@pytest_asyncio.fixture(scope='session')
async def invalid_post_data(fker: Faker) -> list[dict]:
    post_data = gen_post_data(fker, n=4)
    del post_data[0]['content']
    del post_data[1]['title']
    post_data[2]['title'] = ''
    post_data[3]['title'] = _get_random_string(501)

    yield post_data


@pytest_asyncio.fixture(scope='session')
async def user_keys() -> set:
    yield {'id', 'name', 'email', 'created_on', 'updated_on', 'posts'}


@pytest_asyncio.fixture(scope='session')
async def post_keys() -> set:
    yield {'id', 'title', 'content', 'created_on', 'updated_on', 'author'}


@pytest_asyncio.fixture(autouse=True, scope="function")
async def init_db(_init_user_data: list[dict],
                  _init_post_data: list[dict],
                  test_async_db_client: AsyncIOClient) -> tuple:
    query = '''WITH posts := (SELECT (WITH user_raw_data := <json>$user_data,
                                       for user in json_array_unpack(user_raw_data) union (
                                            WITH one_author := (SELECT assert_single((INSERT User {name := <str>user['name'], email :=<str>user['email'] }))),
                                                 post_raw_data := <json>$post_data,
                                            for post in json_array_unpack(post_raw_data) union (
                                                INSERT Post {title:=<str>post['title'], content:=<str>post['content'], author:=one_author})))),
                SELECT posts {id, title, content, created_on, updated_on, author:{
                            id, name, email }};'''

    posts = await test_async_db_client.query_json(query,
                                                  user_data=json.dumps(
                                                      _init_user_data),
                                                  post_data=json.dumps(_init_post_data))

    query = '''SELECT User {id, name, email, created_on, updated_on, posts:{
                            id, title, updated_on }};'''
    users = await test_async_db_client.query_json(query)

    init_users, init_posts = json.loads(users), json.loads(posts)

    print(f'\n{init_db=} called')
    print(f'{len(init_users)=}, {len(init_posts)=}')
    yield init_users, init_posts

    await test_async_db_client.query('DELETE User;')


@pytest.mark.asyncio
class TestUser:
    URL_USERS = '/users'
    URL_USER = '/user'

    async def test_get_valid_users(self,
                                   init_user_n: int,
                                   init_post_n: int,
                                   test_async_client: httpx.AsyncClient):
        url = self.URL_USERS
        resp = await test_async_client.get(url)
        result = resp.json()

        assert resp.status_code == status.HTTP_200_OK
        assert len(result) == init_user_n
        posts = [post
                 for user in result
                 for post in user['posts']]

        assert len(posts) == init_user_n*init_post_n

    async def test_delete_valid_users(self,
                                      init_user_n: int,
                                      test_async_client: httpx.AsyncClient,
                                      test_async_db_client: AsyncIOClient):
        url = self.URL_USERS
        resp = await test_async_client.delete(url)
        result = resp.json()

        assert resp.status_code == status.HTTP_200_OK
        assert len(result) == init_user_n

        # To check all posts are deleted by using `test_async_db_client`
        query = '''SELECT Post;'''
        posts = await test_async_db_client.query(query)

        assert len(posts) == 0

    async def test_get_valid_user(self,
                                  user_keys: set,
                                  init_db: tuple,
                                  init_post_n: int,
                                  test_async_client: httpx.AsyncClient):
        init_users, _ = init_db
        for user in init_users:
            name = user['name']
            url = f'{self.URL_USER}/{name}'
            resp = await test_async_client.get(url)
            result = resp.json()

            assert resp.status_code == status.HTTP_200_OK
            assert user_keys == set(result)
            assert result['id'] == user['id']
            assert result['name'] == name
            assert result['email'] == user['email']
            assert _is_reasonable_updatetime(
                result['created_on'], result['updated_on'])
            assert len(result['posts']) == init_post_n

    async def test_get_invalid_user(self,
                                    init_db: tuple,
                                    fker: Faker,
                                    test_async_client: httpx.AsyncClient):
        init_users, _ = init_db
        for user in init_users:
            name = user['name'] + _get_name(fker)
            url = f'{self.URL_USER}/{name}'
            resp = await test_async_client.get(url)

            assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_post_valid_user(self,
                                   user_keys: set,
                                   valid_user_data: dict,
                                   test_async_client: httpx.AsyncClient):
        url = self.URL_USER
        for payload in valid_user_data:
            resp = await test_async_client.post(url, json=payload)
            result = resp.json()

            assert resp.status_code == status.HTTP_201_CREATED
            assert user_keys == set(result)
            assert result['name'] == payload['name']
            assert result['email'] == payload['email']
            assert _is_reasonable_updatetime(
                result['created_on'], result['updated_on'])
            assert len(result['posts']) == 0

    async def test_post_invalid_user(self,
                                     invalid_user_data: list[dict],
                                     test_async_client: httpx.AsyncClient):
        url = self.URL_USER
        for payload in invalid_user_data:
            resp = await test_async_client.post(url, json=payload)

            assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_post_existing_email(self,
                                       init_db: tuple,
                                       test_async_client: httpx.AsyncClient):
        init_users, _ = init_db
        u0_email = init_users[0]['email']
        payload0 = {'email': u0_email}
        url = self.URL_USER
        for payload in init_users[1:]:
            payload.update(**payload0)
            resp = await test_async_client.post(url, json=payload)

            assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_patch_valid_user(self,
                                    user_keys: set,
                                    init_db: tuple,
                                    fker: Faker,
                                    test_async_client: httpx.AsyncClient,
                                    test_async_db_client: AsyncIOClient):
        init_users, _ = init_db
        for user in init_users:
            name = user['name']
            email = user['email']
            new_email = _get_email(fker)
            payload = {'email': new_email}
            url = f'{self.URL_USER}/{name}'
            resp = await test_async_client.patch(url, json=payload)
            result = resp.json()

            assert resp.status_code == status.HTTP_200_OK
            assert user_keys == set(result)
            assert result['id'] == user['id']
            assert result['name'] == name
            assert result['email'] == new_email
            assert _is_reasonable_updatetime(
                result['created_on'], result['updated_on'])

            query = '''SELECT User FILTER .email=<str>$email;'''
            orig_user = await test_async_db_client.query(query, email=email)

            assert len(orig_user) == 0

    async def test_patch_invalid_user(self,
                                      init_db: tuple,
                                      fker: Faker,
                                      test_async_client: httpx.AsyncClient):

        init_users, _ = init_db
        for user in init_users:
            name = user['name']
            new_email = _get_email(fker).replace('@', '_')
            payload = {'email': new_email}
            url = f'{self.URL_USER}/{name}'
            resp = await test_async_client.patch(url, json=payload)

            assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_delete_valid_user(self,
                                     user_keys: set,
                                     init_db: tuple,
                                     test_async_client: httpx.AsyncClient,
                                     test_async_db_client: AsyncIOClient):
        init_users, _ = init_db
        for user in init_users:
            name = user['name']
            url = f'{self.URL_USER}/{name}'
            resp = await test_async_client.delete(url)
            result = resp.json()

            assert resp.status_code == status.HTTP_200_OK
            assert user_keys == set(result)
            assert result['id'] == user['id']
            assert result['name'] == user['name']
            assert result['email'] == user['email']

            query = '''SELECT User FILTER .name=<str>$name;'''
            delete_user = await test_async_db_client.query(query, name=name)

            assert len(delete_user) == 0

    async def test_delete_invalid_user(self,
                                       init_db: tuple,
                                       fker: Faker,
                                       test_async_client: httpx.AsyncClient):
        init_users, _ = init_db
        for user in init_users:
            name = user['name'] + _get_name(fker)
            url = f'{self.URL_USER}/{name}'
            resp = await test_async_client.delete(url)

            assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
class TestPost:
    URL_POSTS = '/posts'
    URL_POST = '/post'

    async def test_get_valid_posts(self,
                                   init_user_n: int,
                                   init_post_n: int,
                                   test_async_client: httpx.AsyncClient):
        url = self.URL_POSTS
        resp = await test_async_client.get(url)
        result = resp.json()

        assert resp.status_code == status.HTTP_200_OK
        assert len(result) == init_user_n*init_post_n

    async def test_delete_valid_posts(self,
                                      init_user_n: int,
                                      init_post_n: int,
                                      test_async_client: httpx.AsyncClient,
                                      test_async_db_client: AsyncIOClient):
        url = self.URL_POSTS
        resp = await test_async_client.delete(url)
        result = resp.json()

        assert resp.status_code == status.HTTP_200_OK
        assert len(result) == init_user_n*init_post_n

        # To check all posts are deleted by using `test_async_db_client`
        query = '''SELECT Post;'''
        posts = await test_async_db_client.query(query)

        assert len(posts) == 0

        # To check all users are not deleted by using `test_async_db_client`
        query = '''SELECT User;'''
        users = await test_async_db_client.query(query)

        assert len(users) == init_user_n

    async def test_get_valid_post(self,
                                  post_keys: set,
                                  init_db: tuple,
                                  test_async_client: httpx.AsyncClient):
        _, init_posts = init_db
        for post in init_posts:
            pid = post['id']
            url = f'{self.URL_POST}/{pid}'
            resp = await test_async_client.get(url)
            result = resp.json()

            assert resp.status_code == status.HTTP_200_OK
            assert post_keys == set(result)
            assert result['id'] == pid
            assert result['title'] == post['title']
            assert result['content'] == post['content']
            assert _is_reasonable_updatetime(
                result['created_on'], result['updated_on'])
            author = result['author']
            assert author['id'] == post['author']['id']
            assert author['name'] == post['author']['name']
            assert author['email'] == post['author']['email']

    async def test_get_invalid_post(self,
                                    init_db: tuple,
                                    test_async_client: httpx.AsyncClient):
        _, init_posts = init_db
        for _ in init_posts:
            pid = _get_uuid4_str()
            url = f'{self.URL_POST}/{pid}'
            resp = await test_async_client.get(url)

            assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_post_valid_post(self,
                                   post_keys: set,
                                   init_db: tuple,
                                   init_post_n: int,
                                   valid_post_data: dict,
                                   test_async_client: httpx.AsyncClient,
                                   test_async_db_client: AsyncIOClient):
        init_users, _ = init_db
        url = self.URL_POST
        for user in init_users:
            name = user['name']
            params = {'author_name': name}
            for payload in valid_post_data:
                resp = await test_async_client.post(url,
                                                    json=payload,
                                                    params=params)
                result = resp.json()

                assert resp.status_code == status.HTTP_201_CREATED
                assert post_keys == set(result)
                assert _isinstance_uuid4(result['id'])
                assert result['title'] == payload['title']
                assert result['content'] == payload['content']
                assert _is_reasonable_updatetime(
                    result['created_on'], result['updated_on'])
                assert result['author']['name'] == name

            # to make sure the posts are appended
            query = '''SELECT User {posts} FILTER .name=<str>$name;'''
            get_user = await test_async_db_client.query_required_single_json(query, name=name)
            posts = json.loads(get_user)['posts']

            assert len(posts) == init_post_n + len(valid_post_data)

    async def test_post_invalid_post(self,
                                     invalid_post_data: list[dict],
                                     test_async_client: httpx.AsyncClient):
        url = self.URL_POST
        for payload in invalid_post_data:
            resp = await test_async_client.post(url, json=payload)

            assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_patch_valid_post1(self,
                                     post_keys: set,
                                     init_db: tuple,
                                     fker: Faker,
                                     test_async_client: httpx.AsyncClient):
        _, init_posts = init_db
        for post in init_posts:
            pid = post['id']
            new_title, new_content = _get_title(fker), _get_content(fker)
            payload = {'title': new_title, 'content': new_content}
            url = f'{self.URL_POST}/{pid}'
            resp = await test_async_client.patch(url, json=payload)
            result = resp.json()

            assert resp.status_code == status.HTTP_200_OK
            assert post_keys == set(result)
            assert result['id'] == pid
            assert result['title'] == new_title
            assert result['content'] == new_content
            assert _is_reasonable_updatetime(
                result['created_on'], result['updated_on'])

    async def test_patch_valid_post2(self,
                                     post_keys: set,
                                     init_db: tuple,
                                     fker: Faker,
                                     test_async_client: httpx.AsyncClient):
        _, init_posts = init_db
        for post in init_posts:
            pid = post['id']
            content = post['content']
            new_title = _get_title(fker)
            payload = {'title': new_title}
            url = f'{self.URL_POST}/{pid}'
            resp = await test_async_client.patch(url, json=payload)
            result = resp.json()

            assert resp.status_code == status.HTTP_200_OK
            assert post_keys == set(result)
            assert result['id'] == pid
            assert result['title'] == new_title
            assert result['content'] == content
            assert _is_reasonable_updatetime(
                result['created_on'], result['updated_on'])

    async def test_patch_valid_post3(self,
                                     post_keys: set,
                                     init_db: tuple,
                                     fker: Faker,
                                     test_async_client: httpx.AsyncClient):
        _, init_posts = init_db
        for post in init_posts:
            pid = post['id']
            title = post['title']
            new_content = _get_content(fker)
            payload = {'content': new_content}
            url = f'{self.URL_POST}/{pid}'
            resp = await test_async_client.patch(url, json=payload)
            result = resp.json()

            assert resp.status_code == status.HTTP_200_OK
            assert post_keys == set(result)
            assert result['id'] == pid
            assert result['title'] == title
            assert result['content'] == new_content
            assert _is_reasonable_updatetime(
                result['created_on'], result['updated_on'])

    async def test_patch_invalid_post(self,
                                      init_db: tuple,
                                      fker: Faker,
                                      test_async_client: httpx.AsyncClient):
        _, init_posts = init_db
        for post in init_posts:
            pid = post['id']
            new_title, new_content = _get_random_string(
                501), _get_content(fker)
            payload = {'title': new_title, 'content': new_content}
            url = f'{self.URL_POST}/{pid}'
            resp = await test_async_client.patch(url, json=payload)

            assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_delete_valid_post(self,
                                     post_keys: set,
                                     init_db: tuple,
                                     test_async_client: httpx.AsyncClient,
                                     test_async_db_client: AsyncIOClient):
        _, init_posts = init_db
        for post in init_posts:
            pid = post['id']
            url = f'{self.URL_POST}/{pid}'
            resp = await test_async_client.delete(url)
            result = resp.json()

            assert resp.status_code == status.HTTP_200_OK
            assert post_keys == set(result)
            assert result['id'] == post['id']
            assert result['title'] == post['title']
            assert result['content'] == post['content']

            query = '''SELECT Post FILTER .id=<uuid>$id;'''
            delete_post = await test_async_db_client.query(query, id=pid)

            assert len(delete_post) == 0

    async def test_delete_invalid_post(self,
                                       init_db: tuple,
                                       test_async_client: httpx.AsyncClient):
        _, init_posts = init_db
        for _ in init_posts:
            pid = _get_uuid4_str()
            url = f'{self.URL_POST}/{pid}'
            resp = await test_async_client.delete(url)

            assert resp.status_code == status.HTTP_404_NOT_FOUND
