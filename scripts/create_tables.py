import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.db.snowflake import execute
from app.db.sql import load_sql

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


def run_sql_file(name: str) -> None:
    sql = load_sql(name)
    for statement in [s.strip() for s in sql.split(";") if s.strip()]:
        execute(statement)
        logger.info("Executed %s", name)


def main() -> None:
    for name in ["00_setup_check.sql", "01_tables.sql", "05_app_user.sql"]:
        run_sql_file(name)


if __name__ == "__main__":
    main()
