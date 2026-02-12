from typing import Optional

from app.db.snowflake import execute, fetch_one, fetch_all
from app.models.flight import FlightCreate, FlightUpdate


def _normalize(row: Optional[dict]) -> Optional[dict]:
    if not row:
        return None
    return {k.lower(): v for k, v in row.items()}


def _normalize_list(rows: list[dict]) -> list[dict]:
    return [{k.lower(): v for k, v in row.items()} for row in rows]


def create_flight(data: FlightCreate) -> dict:
    sql = """
    INSERT INTO FACT_FLIGHT (
        FLIGHT_NK, FLIGHT_DATE, FLIGHT_STATUS, AIRLINE_IATA, FLIGHT_NUMBER,
        FLIGHT_IATA, FLIGHT_ICAO, DEP_IATA, ARR_IATA, DEP_TERMINAL, DEP_GATE,
        ARR_TERMINAL, ARR_GATE, DEP_DELAY_MIN, ARR_DELAY_MIN,
        DEP_SCHEDULED_UTC, DEP_ESTIMATED_UTC, DEP_ACTUAL_UTC,
        ARR_SCHEDULED_UTC, ARR_ESTIMATED_UTC, ARR_ACTUAL_UTC,
        LAST_SEEN_AT, SOURCE
    )
    VALUES (
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s,
        %s, %s, %s,
        %s, %s, %s,
        CURRENT_TIMESTAMP(), %s
    )
    """
    execute(
        sql,
        (
            data.flight_nk,
            data.flight_date,
            data.flight_status,
            data.airline_iata,
            data.flight_number,
            data.flight_iata,
            data.flight_icao,
            data.dep_iata,
            data.arr_iata,
            data.dep_terminal,
            data.dep_gate,
            data.arr_terminal,
            data.arr_gate,
            data.dep_delay_min,
            data.arr_delay_min,
            data.dep_scheduled_utc,
            data.dep_estimated_utc,
            data.dep_actual_utc,
            data.arr_scheduled_utc,
            data.arr_estimated_utc,
            data.arr_actual_utc,
            data.source,
        ),
    )
    return get_flight(data.flight_nk)


def get_flight(flight_nk: str) -> Optional[dict]:
    sql = "SELECT * FROM FACT_FLIGHT WHERE FLIGHT_NK = %s"
    return _normalize(fetch_one(sql, (flight_nk,)))


def list_flights(
    limit: int,
    offset: int,
    dep_iata: Optional[str] = None,
    arr_iata: Optional[str] = None,
    flight_date: Optional[str] = None,
    status: Optional[str] = None,
) -> tuple[list[dict], int]:
    conditions = []
    params = []
    if dep_iata:
        conditions.append("DEP_IATA = %s")
        params.append(dep_iata)
    if arr_iata:
        conditions.append("ARR_IATA = %s")
        params.append(arr_iata)
    if flight_date:
        conditions.append("FLIGHT_DATE = %s")
        params.append(flight_date)
    if status:
        conditions.append("FLIGHT_STATUS = %s")
        params.append(status)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    total_sql = f"SELECT COUNT(*) AS CNT FROM FACT_FLIGHT {where_clause}"
    total_row = fetch_one(total_sql, params)
    total = int(total_row["CNT"]) if total_row else 0

    list_sql = f"""
    SELECT * FROM FACT_FLIGHT
    {where_clause}
    ORDER BY FLIGHT_DATE DESC
    LIMIT %s OFFSET %s
    """
    rows = fetch_all(list_sql, params + [limit, offset])
    return _normalize_list(rows), total


def update_flight(flight_nk: str, data: FlightUpdate) -> Optional[dict]:
    fields = []
    params = []
    for col, val in {
        "FLIGHT_DATE": data.flight_date,
        "FLIGHT_STATUS": data.flight_status,
        "AIRLINE_IATA": data.airline_iata,
        "FLIGHT_NUMBER": data.flight_number,
        "FLIGHT_IATA": data.flight_iata,
        "FLIGHT_ICAO": data.flight_icao,
        "DEP_IATA": data.dep_iata,
        "ARR_IATA": data.arr_iata,
        "DEP_TERMINAL": data.dep_terminal,
        "DEP_GATE": data.dep_gate,
        "ARR_TERMINAL": data.arr_terminal,
        "ARR_GATE": data.arr_gate,
        "DEP_DELAY_MIN": data.dep_delay_min,
        "ARR_DELAY_MIN": data.arr_delay_min,
        "DEP_SCHEDULED_UTC": data.dep_scheduled_utc,
        "DEP_ESTIMATED_UTC": data.dep_estimated_utc,
        "DEP_ACTUAL_UTC": data.dep_actual_utc,
        "ARR_SCHEDULED_UTC": data.arr_scheduled_utc,
        "ARR_ESTIMATED_UTC": data.arr_estimated_utc,
        "ARR_ACTUAL_UTC": data.arr_actual_utc,
        "SOURCE": data.source,
    }.items():
        if val is not None:
            fields.append(f"{col} = %s")
            params.append(val)
    if not fields:
        return get_flight(flight_nk)

    sql = f"UPDATE FACT_FLIGHT SET {', '.join(fields)}, LAST_SEEN_AT = CURRENT_TIMESTAMP() WHERE FLIGHT_NK = %s"
    params.append(flight_nk)
    execute(sql, params)
    return get_flight(flight_nk)


def delete_flight(flight_nk: str) -> bool:
    sql = "DELETE FROM FACT_FLIGHT WHERE FLIGHT_NK = %s"
    execute(sql, (flight_nk,))
    return True
