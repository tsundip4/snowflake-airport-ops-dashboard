from fastapi import APIRouter, Depends

from app.auth.deps import get_current_user
from app.models.unique import UniqueAirlineResponse
from app.services.uniqueservice import get_unique_airlines

router = APIRouter(prefix="", tags=["unique-airlines"], dependencies=[Depends(get_current_user)])


@router.get("/airports/{iata}/unique-airlines", response_model=UniqueAirlineResponse)
async def unique_airlines(iata: str):
    items = get_unique_airlines(iata)
    return UniqueAirlineResponse(airport_iata=iata, items=items)
