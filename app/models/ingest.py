from pydantic import BaseModel


class IngestResponse(BaseModel):
    ingest_id: str
    raw_inserted: int
    airports_upserted: int
    airlines_upserted: int
    flights_inserted: int
    flights_updated: int
