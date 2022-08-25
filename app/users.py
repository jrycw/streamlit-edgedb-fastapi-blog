import json

import edgedb
from edgedb.asyncio_client import AsyncIOClient
from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.db_clients import get_async_db_client
from app.models import User, UserPatch, UserReq
from app.tags import Tags

router = APIRouter()


@router.get('/users', response_model=list[User], tags=[Tags.USERS])
async def get_users(client: AsyncIOClient = Depends(get_async_db_client)) -> list[User]:
    query = '''SELECT User {id, name, email, created_on, updated_on,
                posts: {id, title, content, created_on, updated_on }};'''
    users = await client.query_json(query)
    return json.loads(users)


@router.delete('/users', response_model=list[User], tags=[Tags.USERS])
async def delete_users(client: AsyncIOClient = Depends(get_async_db_client)) -> list[User]:
    query = '''WITH delete_users := (SELECT (DELETE User))
                SELECT delete_users {id, name, email, created_on, updated_on,
                posts: {id, title, content, created_on, updated_on }};'''
    deleted_users = await client.query_json(query)
    return json.loads(deleted_users)


@router.get('/user/{name}', response_model=User, tags=[Tags.USERS])
async def get_user(name: str = Path(min_length=1, max_length=100),
                   client: AsyncIOClient = Depends(get_async_db_client)) -> User:
    try:
        query = '''WITH get_user := (SELECT assert_single((SELECT User FILTER .name=<str>$name)))
                    SELECT get_user {id, name, email, created_on, updated_on,
                    posts: {id, title, content, updated_on }};'''

        user = await client.query_required_single_json(query, name=name)
    except edgedb.errors.NoDataError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={'error': f"User(name = '{name}') not found"})
    return json.loads(user)


@router.post('/user', response_model=User, status_code=status.HTTP_201_CREATED, tags=[Tags.USERS])
async def post_user(user: UserReq, client: AsyncIOClient = Depends(get_async_db_client)) -> User:
    try:
        query = '''WITH new_user := (INSERT User {name := <str>$name, email :=<str>$email})
                    SELECT new_user {id, name, email, created_on, updated_on, posts};'''
        created_user = await client.query_required_single_json(query,
                                                               name=user.name,
                                                               email=user.email)
    except edgedb.errors.ConstraintViolationError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail={'error': f'{user.name} or/and "{user.email}"\
                                 might be occupied!)'})
    return json.loads(created_user)


@router.patch('/user/{name}', response_model=User, tags=[Tags.USERS])
async def patch_user(user: UserPatch,
                     name: str = Path(min_length=1, max_length=100),
                     client: AsyncIOClient = Depends(get_async_db_client)) -> User:
    try:
        filter_name = name
        if user.email:
            query = '''WITH patch_user := (SELECT assert_single((Update User FILTER .name=<str>$filter_name
                        SET {email:=<str>$email, updated_on:=datetime_current()})))
                        SELECT patch_user {id, name, email, created_on, updated_on,
                        posts: {id, title, content, updated_on }};'''
            patched_user = await client.query_required_single_json(query,
                                                                   email=user.email,
                                                                   filter_name=filter_name)
        else:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail={'error': f"must specify the email field"})
    except edgedb.errors.NoDataError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={'error': f"User(name = '{filter_name}') not found"})
    except edgedb.errors.ConstraintViolationError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail={'error': f"{user.email} has been occupied!)"})
    return json.loads(patched_user)


@router.delete('/user/{name}',  response_model=User, tags=[Tags.USERS])
async def delete_user(name: str = Path(min_length=1, max_length=100),
                      client: AsyncIOClient = Depends(get_async_db_client)) -> User:
    try:
        query = '''WITH delete_user := (SELECT assert_single((DELETE User FILTER .name=<str>$name)))
                    SELECT delete_user {id, name, email, created_on, updated_on,
                    posts: {id, title, content, updated_on }};'''
        deleted_user = await client.query_required_single_json(query, name=name)
    except edgedb.errors.NoDataError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={'error': f"User(name = '{name}') not found"})
    return json.loads(deleted_user)
