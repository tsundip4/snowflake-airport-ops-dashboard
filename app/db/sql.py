from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
SQL_DIR = BASE_DIR / "sql"


def load_sql(filename: str) -> str:
    path = SQL_DIR / filename
    return path.read_text()
