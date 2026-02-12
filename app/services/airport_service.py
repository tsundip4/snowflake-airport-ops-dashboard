from typing import Optional

from app.db.snowflake import execute, fetch_one, fetch_all
from app.models.airport import AirportCreate, AirportUpdate


def _normalize(row: Optional[dict]) -> Optional[dict]:
    if not row:
        return None
    return {k.lower(): v for k, v in row.items()}


def _normalize_list(rows: list[dict]) -> list[dict]:
    return [{k.lower(): v for k, v in row.items()} for row in rows]


def create_airport(data: AirportCreate) -> dict:
    sql = """
    INSERT INTO DIM_AIRPORT (AIRPORT_IATA, AIRPORT_NAME, TIMEZONE, ICAO, UPDATED_AT)
    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP())
    """
    execute(sql, (data.airport_iata, data.airport_name, data.timezone, data.icao))
    return get_airport(data.airport_iata)


def get_airport(iata: str) -> Optional[dict]:
    sql = "SELECT * FROM DIM_AIRPORT WHERE AIRPORT_IATA = %s"
    return _normalize(fetch_one(sql, (iata,)))


def list_airports(limit: int, offset: int) -> tuple[list[dict], int]:
    total_row = fetch_one("SELECT COUNT(*) AS CNT FROM DIM_AIRPORT")
    total = int(total_row["CNT"]) if total_row else 0
    sql = """
    SELECT * FROM DIM_AIRPORT
    ORDER BY AIRPORT_IATA
    LIMIT %s OFFSET %s
    """
    rows = fetch_all(sql, (limit, offset))
    return _normalize_list(rows), total


def update_airport(iata: str, data: AirportUpdate) -> Optional[dict]:
    fields = []
    params = []
    if data.airport_name is not None:
        fields.append("AIRPORT_NAME = %s")
        params.append(data.airport_name)
    if data.timezone is not None:
        fields.append("TIMEZONE = %s")
        params.append(data.timezone)
    if data.icao is not None:
        fields.append("ICAO = %s")
        params.append(data.icao)
    if not fields:
        return get_airport(iata)

    sql = f"UPDATE DIM_AIRPORT SET {', '.join(fields)}, UPDATED_AT = CURRENT_TIMESTAMP() WHERE AIRPORT_IATA = %s"
    params.append(iata)
    execute(sql, params)
    return get_airport(iata)


def delete_airport(iata: str) -> bool:
    sql = "DELETE FROM DIM_AIRPORT WHERE AIRPORT_IATA = %s"
    execute(sql, (iata,))
    return True
