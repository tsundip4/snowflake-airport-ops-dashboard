import logging
import os
import sys
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.auth.password import hash_password
from app.db.snowflake import execute

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    email = os.getenv("DEMO_EMAIL")
    password = os.getenv("DEMO_PASSWORD")
    if not email or not password:
        raise SystemExit("DEMO_EMAIL and DEMO_PASSWORD must be set")

    password_hash = hash_password(password)
    user_id = str(uuid4())

    sql = """
    MERGE INTO APP_USER AS t
    USING (SELECT %s AS EMAIL, %s AS PASSWORD_HASH, %s AS ID) AS s
    ON t.EMAIL = s.EMAIL
    WHEN MATCHED THEN UPDATE SET PASSWORD_HASH = s.PASSWORD_HASH
    WHEN NOT MATCHED THEN INSERT (ID, EMAIL, PASSWORD_HASH, CREATED_AT)
    VALUES (s.ID, s.EMAIL, s.PASSWORD_HASH, CURRENT_TIMESTAMP())
    """
    execute(sql, (email, password_hash, user_id))
    logger.info("Seeded user %s", email)


if __name__ == "__main__":
    main()
