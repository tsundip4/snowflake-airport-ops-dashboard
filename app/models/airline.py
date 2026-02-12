from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AirlineBase(BaseModel):
    airline_iata: str = Field(..., min_length=2, max_length=3)
    airline_icao: Optional[str] = None
    airline_name: Optional[str] = None


class AirlineCreate(AirlineBase):
    pass


class AirlineUpdate(BaseModel):
    airline_icao: Optional[str] = None
    airline_name: Optional[str] = None


class AirlineOut(AirlineBase):
    updated_at: Optional[datetime] = None


class AirlineList(BaseModel):
    items: list[AirlineOut]
    total: int
    limit: int
    offset: int
