import logging
from contextlib import contextmanager
from typing import Any, Iterable, Optional

import snowflake.connector

from app.config import get_settings

logger = logging.getLogger(__name__)


@contextmanager
def get_connection():
    settings = get_settings()
    conn = snowflake.connector.connect(
        account=settings.snowflake_account,
        user=settings.snowflake_user,
        password=settings.snowflake_password,
        role=settings.snowflake_role or None,
        warehouse=settings.snowflake_warehouse or None,
        database=settings.snowflake_database or None,
        schema=settings.snowflake_schema or None,
    )
    try:
        # Ensure session context even if envs were empty on connect
        with conn.cursor() as cur:
            if settings.snowflake_warehouse:
                cur.execute(f"USE WAREHOUSE {settings.snowflake_warehouse}")
            if settings.snowflake_database:
                cur.execute(f"USE DATABASE {settings.snowflake_database}")
            if settings.snowflake_schema:
                cur.execute(f"USE SCHEMA {settings.snowflake_schema}")
        yield conn
    finally:
        conn.close()


@contextmanager
def get_cursor():
    with get_connection() as conn:
        cur = conn.cursor(snowflake.connector.DictCursor)
        try:
            yield cur
            conn.commit()
        finally:
            cur.close()


def execute(sql: str, params: Optional[Iterable[Any]] = None) -> None:
    with get_cursor() as cur:
        cur.execute(sql, params)


def execute_many(sql: str, params_seq: Iterable[Iterable[Any]]) -> None:
    with get_cursor() as cur:
        cur.executemany(sql, params_seq)


def fetch_one(sql: str, params: Optional[Iterable[Any]] = None) -> Optional[dict]:
    with get_cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def fetch_all(sql: str, params: Optional[Iterable[Any]] = None) -> list[dict]:
    with get_cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()
