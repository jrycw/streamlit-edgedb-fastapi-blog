import json
import uuid

import edgedb
from edgedb.asyncio_client import AsyncIOClient
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db_clients import get_async_db_client
from app.models import Post, PostPatch, PostReq
from app.tags import Tags

router = APIRouter()


@router.get('/posts', response_model=list[Post], tags=[Tags.POSTS])
async def get_posts(client: AsyncIOClient = Depends(get_async_db_client)) -> list[Post]:
    query = '''SELECT Post {id, title, content, created_on, updated_on,
                author: {id, name, email }};'''
    posts = await client.query_json(query)
    return json.loads(posts)


@router.delete('/posts', response_model=list[Post], tags=[Tags.POSTS])
async def delete_posts(client: AsyncIOClient = Depends(get_async_db_client)) -> list[Post]:
    query = '''WITH delete_posts := (SELECT (DELETE Post))
                SELECT delete_posts {id, title, content, created_on, updated_on,
                author: {id, name, email }};'''
    deleted_posts = await client.query_json(query)
    return json.loads(deleted_posts)


@router.get('/post/{id}', response_model=Post, tags=[Tags.POSTS])
async def get_post(id: uuid.UUID,
                   client: AsyncIOClient = Depends(get_async_db_client)) -> Post:
    try:
        query = '''WITH get_post := (SELECT assert_single((SELECT Post FILTER .id=<uuid>$id)))
                    SELECT get_post {id, title, content, created_on, updated_on,
                    author: {id, name, email }};'''
        post = await client.query_required_single_json(query, id=id)
    except edgedb.errors.NoDataError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={'error': f"Post(id = '{id}') not found"})
    return json.loads(post)


@router.post('/post', response_model=Post, status_code=status.HTTP_201_CREATED, tags=[Tags.POSTS])
async def post_post(post: PostReq,
                    author_name: str = Query(min_length=1, max_length=100),
                    client: AsyncIOClient = Depends(get_async_db_client)) -> Post:
    query = '''WITH the_author := (SELECT assert_single((SELECT User FILTER .name=<str>$name))),
                    new_post := (INSERT Post {title := <str>$title, content :=<str>$content, author:=the_author})
                SELECT new_post {id, title, content, created_on, updated_on,
                    author: {id, name, email }};'''
    created_user = await client.query_required_single_json(query,
                                                           name=author_name,
                                                           title=post.title,
                                                           content=post.content)
    return json.loads(created_user)


@router.patch('/post/{id}', response_model=Post, tags=[Tags.POSTS])
async def patch_post(post: PostPatch,
                     id: uuid.UUID,
                     client: AsyncIOClient = Depends(get_async_db_client)) -> Post:
    try:
        filter_id = id
        if post.title and post.content:
            query = '''WITH patched_post := (SELECT assert_single((Update Post FILTER .id=<uuid>$filter_id
                        SET {title:=<str>$title, content:=<str>$content, updated_on:=datetime_current()})))
                        SELECT patched_post {id, title, content, created_on, updated_on,
                        author: {id, name, email }};'''
            patched_post = await client.query_required_single_json(query,
                                                                   title=post.title,
                                                                   content=post.content,
                                                                   filter_id=filter_id)
        elif not post.title:
            query = '''WITH patched_post := (SELECT assert_single((Update Post FILTER .id=<uuid>$filter_id
                        SET {content:=<str>$content, updated_on:=datetime_current()})))
                        SELECT patched_post {id, title, content, created_on, updated_on,
                        author: {id, name, email }};'''
            patched_post = await client.query_required_single_json(query,
                                                                   content=post.content,
                                                                   filter_id=filter_id)
        elif not post.content:
            query = '''WITH patched_post := (SELECT assert_single((Update Post FILTER .id=<uuid>$filter_id
                                    SET {title:=<str>$title, updated_on:=datetime_current()})))
                                    SELECT patched_post {id, title, content, created_on, updated_on,
                                    author: {id, name, email }};'''
            patched_post = await client.query_required_single_json(query,
                                                                   title=post.title,
                                                                   filter_id=filter_id)

        else:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail={'error': f"must specify at least {post.title} or {post.content}"})
    except edgedb.errors.NoDataError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={'error': f"Post(id = '{filter_id}') not found"})
    return json.loads(patched_post)


@router.delete('/post/{id}',  response_model=Post, tags=[Tags.POSTS])
async def delete_post(id: uuid.UUID,
                      client: AsyncIOClient = Depends(get_async_db_client)) -> Post:
    try:
        query = '''WITH delete_post := (SELECT assert_single((DELETE Post FILTER .id=<uuid>$id)))
                    SELECT delete_post {id, title, content, created_on, updated_on, 
                    author: {id, name, email }};'''
        deleted_post = await client.query_required_single_json(query, id=id)
    except edgedb.errors.NoDataError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={'error': f"Post(id = '{id}') not found"})
    return json.loads(deleted_post)
