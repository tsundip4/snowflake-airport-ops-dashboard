from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.deps import get_current_user
from app.models.airline import AirlineCreate, AirlineList, AirlineOut, AirlineUpdate
from app.services.airline_service import (
    create_airline,
    delete_airline,
    get_airline,
    list_airlines,
    update_airline,
)

router = APIRouter(prefix="/airlines", tags=["airlines"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=AirlineOut, status_code=status.HTTP_201_CREATED)
async def create(payload: AirlineCreate):
    return create_airline(payload)


@router.get("/{iata}", response_model=AirlineOut)
async def get_one(iata: str):
    row = get_airline(iata)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Airline not found")
    return row


@router.get("", response_model=AirlineList)
async def list_all(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    rows, total = list_airlines(limit, offset)
    return AirlineList(items=rows, total=total, limit=limit, offset=offset)


@router.put("/{iata}", response_model=AirlineOut)
async def update(iata: str, payload: AirlineUpdate):
    row = update_airline(iata, payload)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Airline not found")
    return row


@router.delete("/{iata}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(iata: str):
    delete_airline(iata)
    return None
