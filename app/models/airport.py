from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AirportBase(BaseModel):
    airport_iata: str = Field(..., min_length=3, max_length=4)
    airport_name: Optional[str] = None
    timezone: Optional[str] = None
    icao: Optional[str] = None


class AirportCreate(AirportBase):
    pass


class AirportUpdate(BaseModel):
    airport_name: Optional[str] = None
    timezone: Optional[str] = None
    icao: Optional[str] = None


class AirportOut(AirportBase):
    updated_at: Optional[datetime] = None


class AirportList(BaseModel):
    items: list[AirportOut]
    total: int
    limit: int
    offset: int
