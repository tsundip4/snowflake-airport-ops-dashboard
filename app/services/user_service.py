import logging
import uuid
from typing import Optional

from app.auth.password import verify_password
from app.db.snowflake import execute, fetch_one

logger = logging.getLogger(__name__)


def get_user_by_email(email: str) -> Optional[dict]:
    sql = "SELECT ID, EMAIL, PASSWORD_HASH, CREATED_AT FROM APP_USER WHERE EMAIL = %s"
    return fetch_one(sql, (email,))


def authenticate_user(email: str, password: str) -> Optional[dict]:
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user["PASSWORD_HASH"]):
        return None
    return user


def get_or_create_user_by_email(email: str) -> dict:
    user = get_user_by_email(email)
    if user:
        return user

    user_id = str(uuid.uuid4())
    sql = "INSERT INTO APP_USER (ID, EMAIL, PASSWORD_HASH, CREATED_AT) VALUES (%s, %s, %s, CURRENT_TIMESTAMP())"
    execute(sql, (user_id, email, None))
    return get_user_by_email(email)
