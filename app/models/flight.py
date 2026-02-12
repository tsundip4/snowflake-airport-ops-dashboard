from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class FlightBase(BaseModel):
    flight_nk: Optional[str] = None
    flight_date: Optional[date] = None
    flight_status: Optional[str] = None
    airline_iata: Optional[str] = None
    flight_number: Optional[str] = None
    flight_iata: Optional[str] = None
    flight_icao: Optional[str] = None
    dep_iata: Optional[str] = None
    arr_iata: Optional[str] = None
    dep_terminal: Optional[str] = None
    dep_gate: Optional[str] = None
    arr_terminal: Optional[str] = None
    arr_gate: Optional[str] = None
    dep_delay_min: Optional[int] = None
    arr_delay_min: Optional[int] = None
    dep_scheduled_utc: Optional[datetime] = None
    dep_estimated_utc: Optional[datetime] = None
    dep_actual_utc: Optional[datetime] = None
    arr_scheduled_utc: Optional[datetime] = None
    arr_estimated_utc: Optional[datetime] = None
    arr_actual_utc: Optional[datetime] = None
    source: Optional[str] = None


class FlightCreate(FlightBase):
    flight_nk: str = Field(..., min_length=5)
    flight_date: date
    flight_iata: Optional[str] = None
    dep_iata: str
    arr_iata: str


class FlightUpdate(FlightBase):
    pass


class FlightOut(FlightBase):
    last_seen_at: Optional[datetime] = None


class FlightList(BaseModel):
    items: list[FlightOut]
    total: int
    limit: int
    offset: int
