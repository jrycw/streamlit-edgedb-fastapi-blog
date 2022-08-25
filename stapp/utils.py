from datetime import datetime
from enum import Enum
from functools import partial

from config import LOCAL_TZ


def to_tz(datetime_string: str,
          fmt: str = '%Y/%m/%d %H:%M:%S',
          my_tz=LOCAL_TZ) -> str:
    return (datetime
            .fromisoformat(datetime_string)
            .astimezone(my_tz)
            .strftime(fmt))


class DatetimeKey(str, Enum):
    CREATED_ON = 'created_on'
    UPDATED_ON = 'updated_on'


def datetime_sorted_key(u, dkey: DatetimeKey) -> datetime:
    return datetime.fromisoformat(u[dkey])


def get_sort_by_updated_on() -> datetime:
    return partial(datetime_sorted_key, dkey=DatetimeKey.UPDATED_ON)


def get_sort_by_created_on() -> datetime:
    return partial(datetime_sorted_key, dkey=DatetimeKey.CREATED_ON)


def get_excerpt(content: str, n_word=10) -> str:
    return ' '.join(content.split()[:n_word])
