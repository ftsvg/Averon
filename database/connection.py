import functools
import pymysql
from pymysql.cursors import Cursor

from config import Settings


def db_connect():
    return pymysql.connect(
        host=Settings.DBENDPOINT,
        port=3306,
        user=Settings.DBUSER,
        password=Settings.DBPASS,
        database=Settings.DBNAME,
        autocommit=True
    )


def ensure_cursor(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cursor: Cursor | None = kwargs.get("cursor")
        if cursor:
            return func(*args, **kwargs)

        with db_connect() as conn:
            cursor = conn.cursor()
            kwargs["cursor"] = cursor
            return func(*args, **kwargs)

    return wrapper


def async_ensure_cursor(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        cursor: Cursor | None = kwargs.get('cursor')
        if cursor:
            return await func(*args, **kwargs)

        with db_connect() as conn:
            cursor = conn.cursor()
            kwargs['cursor'] = cursor
            return await func(*args, **kwargs)

    return wrapper