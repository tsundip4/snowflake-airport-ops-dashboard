from app.db.snowflake import fetch_all


def get_unique_airlines(airport_iata: str) -> list[dict]:
    sql = f"""
    SELECT DISTINCT
        a.AIRLINE_IATA AS "airline_iata",
        a.AIRLINE_NAME AS "airline_name"
    FROM FACT_FLIGHT f
    JOIN DIM_AIRLINE a ON f.AIRLINE_IATA = a.AIRLINE_IATA
    WHERE f.DEP_IATA = %s OR f.ARR_IATA = %s
    ORDER BY a.AIRLINE_IATA
    """
    return fetch_all(sql, (airport_iata, airport_iata))
