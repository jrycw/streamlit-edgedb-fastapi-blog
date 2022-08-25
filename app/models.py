from datetime import datetime
from typing import Union

from pydantic import BaseModel, EmailStr, Field, validator

from app.utils import format_title


class CreatedTimestamp(BaseModel):
    created_on: Union[datetime, None]


class UpdatedTimestamp(BaseModel):
    updated_on: Union[datetime, None]


class AutoTimestamp(CreatedTimestamp, UpdatedTimestamp):
    pass


class UserBase(AutoTimestamp):
    id: str


class UserReq(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr


class UserResp(UserReq):
    id: str


class UserDefault(UserBase, UserReq):
    pass


class UserPatch(BaseModel):
    email: EmailStr


class PostBase(AutoTimestamp):
    id: str


class PostReq(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str

    @validator('title')
    def format_title(cls, v: str) -> str:
        return format_title(v)


class PostResp(PostBase, PostReq):
    id: str


class PostDefault(PostBase, PostReq):
    pass


class PostPatch(BaseModel):
    title: Union[str, None] = Field(min_length=1, max_length=100)
    content: Union[str, None]

    @validator('title')
    def format_title(cls, v: str) -> str:
        return format_title(v)


class User(UserDefault):
    posts: list[PostResp]


class Post(PostDefault):
    author: UserResp
