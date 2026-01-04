import os
import functools
import pymysql
from pymysql.cursors import Cursor

from dotenv import load_dotenv

load_dotenv()


def _get_database_credentials() -> tuple[str, str, str, str]:
    db_username = os.getenv('DBUSER')
    db_password = os.getenv('DBPASS')
    db_name = os.getenv('DBNAME')
    db_endpoint = os.getenv('DBENDPOINT')
    
    return db_username, db_password, db_name, db_endpoint


def db_connect():
    db_username, db_password, db_name, db_endpoint = _get_database_credentials()
    conn = pymysql.connect(
        host=db_endpoint,
        port=3306,
        user=db_username,
        password=db_password,
        database=db_name,
        autocommit=True
    )
    return conn


def ensure_cursor(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cursor: Cursor | None = kwargs.get('cursor')
        if cursor:
            return func(*args, **kwargs)

        with db_connect() as conn:
            conn.autocommit = True
            cursor = conn.cursor()
            kwargs['cursor'] = cursor
            return func(*args, **kwargs)

    return wrapper


def async_ensure_cursor(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        cursor: Cursor | None = kwargs.get('cursor')
        if cursor:
            return await func(*args, **kwargs)

        with db_connect() as conn:
            conn.autocommit = True
            cursor = conn.cursor()
            kwargs['cursor'] = cursor
            return await func(*args, **kwargs)

    return wrapper