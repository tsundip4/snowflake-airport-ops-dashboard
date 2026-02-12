from typing import Optional

from pydantic import BaseModel


class UniqueAirlineItem(BaseModel):
    airline_iata: str
    airline_name: Optional[str] = None


class UniqueAirlineResponse(BaseModel):
    airport_iata: str
    items: list[UniqueAirlineItem]
