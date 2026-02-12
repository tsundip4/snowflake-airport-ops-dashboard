import json
import logging

import requests

from app.config import get_settings
from app.db.snowflake import fetch_all

logger = logging.getLogger(__name__)


def _fetch_flight_context(limit: int = 50) -> list[dict]:
    sql = """
    SELECT *
    FROM FACT_FLIGHT
    ORDER BY LAST_SEEN_AT DESC
    LIMIT %s
    """
    return fetch_all(sql, (limit,))


def _build_prompt(question: str, flights: list[dict]) -> str:
    data_blob = json.dumps(flights, default=str)
    return (
        "You are a data assistant for an airport operations dashboard. "
        "Answer ONLY using the provided flight data. If the data is insufficient, say so.\n\n"
        f"Question: {question}\n\n"
        f"Flight data (last 50 rows, most recent first, JSON):\n{data_blob}"
    )


def ask_ai(question: str) -> tuple[str, str]:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not set")

    flights = _fetch_flight_context()
    prompt = _build_prompt(question, flights)

    model = settings.gemini_model
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    resp = requests.post(
        url,
        params={"key": settings.gemini_api_key},
        json={
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ]
        },
        timeout=30,
    )
    if resp.status_code == 429:
        raise RuntimeError("Gemini rate limit exceeded. Please try again later.")
    resp.raise_for_status()
    payload = resp.json()
    try:
        answer = payload["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        logger.exception("Unexpected Gemini response: %s", payload)
        answer = "Sorry, I couldn't parse a response from the AI model."

    return answer, model
