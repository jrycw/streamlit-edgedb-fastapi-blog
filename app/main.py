from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.basic import router as basic_router
from app.posts import router as posts_router
from app.users import router as users_router

api = FastAPI()

api.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'])

api.include_router(basic_router)
api.include_router(users_router)
api.include_router(posts_router)
