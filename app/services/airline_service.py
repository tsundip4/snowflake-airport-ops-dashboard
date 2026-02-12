from typing import Optional

from app.db.snowflake import execute, fetch_all, fetch_one
from app.models.airline import AirlineCreate, AirlineUpdate


def _normalize(row: Optional[dict]) -> Optional[dict]:
    if not row:
        return None
    return {k.lower(): v for k, v in row.items()}


def _normalize_list(rows: list[dict]) -> list[dict]:
    return [{k.lower(): v for k, v in row.items()} for row in rows]


def create_airline(data: AirlineCreate) -> dict:
    sql = """
    INSERT INTO DIM_AIRLINE (AIRLINE_IATA, AIRLINE_ICAO, AIRLINE_NAME, UPDATED_AT)
    VALUES (%s, %s, %s, CURRENT_TIMESTAMP())
    """
    execute(sql, (data.airline_iata, data.airline_icao, data.airline_name))
    return get_airline(data.airline_iata)


def get_airline(iata: str) -> Optional[dict]:
    sql = "SELECT * FROM DIM_AIRLINE WHERE AIRLINE_IATA = %s"
    return _normalize(fetch_one(sql, (iata,)))


def list_airlines(limit: int, offset: int) -> tuple[list[dict], int]:
    total_row = fetch_one("SELECT COUNT(*) AS CNT FROM DIM_AIRLINE")
    total = int(total_row["CNT"]) if total_row else 0
    sql = """
    SELECT * FROM DIM_AIRLINE
    ORDER BY AIRLINE_IATA
    LIMIT %s OFFSET %s
    """
    rows = fetch_all(sql, (limit, offset))
    return _normalize_list(rows), total


def update_airline(iata: str, data: AirlineUpdate) -> Optional[dict]:
    fields = []
    params = []
    if data.airline_icao is not None:
        fields.append("AIRLINE_ICAO = %s")
        params.append(data.airline_icao)
    if data.airline_name is not None:
        fields.append("AIRLINE_NAME = %s")
        params.append(data.airline_name)
    if not fields:
        return get_airline(iata)

    sql = f"UPDATE DIM_AIRLINE SET {', '.join(fields)}, UPDATED_AT = CURRENT_TIMESTAMP() WHERE AIRLINE_IATA = %s"
    params.append(iata)
    execute(sql, params)
    return get_airline(iata)


def delete_airline(iata: str) -> bool:
    sql = "DELETE FROM DIM_AIRLINE WHERE AIRLINE_IATA = %s"
    execute(sql, (iata,))
    return True
