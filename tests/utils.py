import random
import uuid
from datetime import datetime
from string import ascii_lowercase
from uuid import uuid4

from app.models import PostReq, UserReq
from app.utils import format_title
from faker import Faker


def _get_random_string(k):
    return ''.join(random.choices(ascii_lowercase, k=k))


def _get_uuid4_str() -> str:
    return str(uuid4())


def _get_name(fker: Faker) -> str:
    return fker.unique.name()


def _get_email(fker: Faker) -> str:
    return fker.unique.email()


def _get_title(fker: Faker) -> str:
    return format_title(' '.join(fker.words(random.randint(2, 10))))


def _get_content(fker: Faker) -> str:
    return fker.paragraph(nb_sentences=5)


def _isinstance_uuid4(one_string: str) -> bool:
    return isinstance(uuid.UUID(one_string), uuid.UUID)


def _is_reasonable_updatetime(created_on, updated_on):
    created_on = datetime.fromisoformat(created_on)
    updated_on = datetime.fromisoformat(updated_on)
    return created_on <= updated_on


def gen_user_data(fker: Faker, n: int = 1) -> list[dict]:
    user_data = [{'name': _get_name(fker),
                  'email': _get_email(fker)}
                 for _ in range(n)]
    return [UserReq(**user).dict()
            for user in user_data]


def gen_post_data(fker: Faker, n: int = 1) -> list[dict]:
    post_data = [{'title': _get_title(fker),
                  'content': _get_content(fker)}
                 for _ in range(n)]
    return [PostReq(**post).dict()
            for post in post_data]
