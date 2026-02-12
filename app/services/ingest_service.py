import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

import requests

from app.config import get_settings
from app.db.snowflake import get_connection
from app.db.sql import load_sql

logger = logging.getLogger(__name__)

MERGE_AIRPORT_SQL = load_sql("02_merge_dim_airport.sql")
MERGE_AIRLINE_SQL = load_sql("03_merge_dim_airline.sql")
MERGE_FLIGHT_SQL = load_sql("04_merge_fact_flight.sql")


def parse_ts(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    if dt.tzinfo:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def ingest_flights(dep_iata: str | None, arr_iata: str | None, limit: int) -> dict:
    settings = get_settings()
    if not settings.aviationstack_access_key:
        raise ValueError("AVIATIONSTACK_ACCESS_KEY is not set")
    if not dep_iata and not arr_iata:
        raise ValueError("Provide dep_iata and/or arr_iata")

    url = "https://api.aviationstack.com/v1/flights"
    params = {
        "access_key": settings.aviationstack_access_key,
        "limit": limit,
    }
    if dep_iata:
        params["dep_iata"] = dep_iata
    if arr_iata:
        params["arr_iata"] = arr_iata
    resp = requests.get(
        url,
        params=params,
        timeout=30,
    )
    resp.raise_for_status()
    payload = resp.json()
    data = payload.get("data", [])

    ingest_id = str(uuid4())
    ingested_at = datetime.now(timezone.utc)

    raw_inserted = 0
    airports = {}
    airlines = {}
    flights_upserted = 0

    with get_connection() as conn:
        cur = conn.cursor()
        try:
            for record in data:
                flight_date = record.get("flight_date")
                flight = record.get("flight", {}) or {}
                departure = record.get("departure", {}) or {}
                arrival = record.get("arrival", {}) or {}
                airline = record.get("airline", {}) or {}

                flight_iata = flight.get("iata")
                dep_iata_val = departure.get("iata")
                arr_iata_val = arrival.get("iata")

                insert_raw_sql = """
                INSERT INTO RAW_AVSTACK_FLIGHTS (
                    INGEST_ID, INGESTED_AT, FLIGHT_DATE, FLIGHT_IATA,
                    DEP_IATA, ARR_IATA, RECORD, SOURCE
                )
                SELECT %s, %s, %s, %s, %s, %s, PARSE_JSON(%s), %s
                """
                cur.execute(
                    insert_raw_sql,
                    (
                        ingest_id,
                        ingested_at,
                        flight_date,
                        flight_iata,
                        dep_iata_val,
                        arr_iata_val,
                        json.dumps(record, ensure_ascii=False),
                        "aviationstack",
                    ),
                )
                raw_inserted += 1

                if dep_iata_val:
                    airports[dep_iata_val] = {
                        "iata": dep_iata_val,
                        "name": departure.get("airport"),
                        "timezone": departure.get("timezone"),
                        "icao": departure.get("icao"),
                    }
                if arr_iata_val:
                    airports[arr_iata_val] = {
                        "iata": arr_iata_val,
                        "name": arrival.get("airport"),
                        "timezone": arrival.get("timezone"),
                        "icao": arrival.get("icao"),
                    }
                if airline.get("iata"):
                    airlines[airline.get("iata")] = {
                        "iata": airline.get("iata"),
                        "icao": airline.get("icao"),
                        "name": airline.get("name"),
                    }

                flight_nk = None
                if flight_iata and flight_date:
                    flight_nk = f"{flight_iata}:{flight_date}"

                if not flight_nk:
                    logger.warning("Skipping flight without key: %s", record)
                    continue

                cur.execute(
                    MERGE_FLIGHT_SQL,
                    (
                        flight_nk,
                        flight_date,
                        record.get("flight_status"),
                        airline.get("iata"),
                        flight.get("number"),
                        flight_iata,
                        flight.get("icao"),
                        dep_iata_val,
                        arr_iata_val,
                        departure.get("terminal"),
                        departure.get("gate"),
                        arrival.get("terminal"),
                        arrival.get("gate"),
                        departure.get("delay"),
                        arrival.get("delay"),
                        parse_ts(departure.get("scheduled")),
                        parse_ts(departure.get("estimated")),
                        parse_ts(departure.get("actual")),
                        parse_ts(arrival.get("scheduled")),
                        parse_ts(arrival.get("estimated")),
                        parse_ts(arrival.get("actual")),
                        "aviationstack",
                    ),
                )
                flights_upserted += 1

            for airport in airports.values():
                cur.execute(
                    MERGE_AIRPORT_SQL,
                    (
                        airport["iata"],
                        airport.get("name"),
                        airport.get("timezone"),
                        airport.get("icao"),
                    ),
                )

            for airline in airlines.values():
                cur.execute(
                    MERGE_AIRLINE_SQL,
                    (
                        airline["iata"],
                        airline.get("icao"),
                        airline.get("name"),
                    ),
                )
            conn.commit()
        finally:
            cur.close()

    return {
        "ingest_id": ingest_id,
        "raw_inserted": raw_inserted,
        "airports_upserted": len(airports),
        "airlines_upserted": len(airlines),
        "flights_inserted": 0,
        "flights_updated": flights_upserted,
    }
