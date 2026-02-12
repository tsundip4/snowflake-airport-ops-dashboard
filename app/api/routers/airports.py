from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.deps import get_current_user
from app.models.airport import AirportCreate, AirportList, AirportOut, AirportUpdate
from app.services.airport_service import (
    create_airport,
    delete_airport,
    get_airport,
    list_airports,
    update_airport,
)

router = APIRouter(prefix="/airports", tags=["airports"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=AirportOut, status_code=status.HTTP_201_CREATED)
async def create(payload: AirportCreate):
    return create_airport(payload)


@router.get("/{iata}", response_model=AirportOut)
async def get_one(iata: str):
    row = get_airport(iata)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Airport not found")
    return row


@router.get("", response_model=AirportList)
async def list_all(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    rows, total = list_airports(limit, offset)
    return AirportList(items=rows, total=total, limit=limit, offset=offset)


@router.put("/{iata}", response_model=AirportOut)
async def update(iata: str, payload: AirportUpdate):
    row = update_airport(iata, payload)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Airport not found")
    return row


@router.delete("/{iata}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(iata: str):
    delete_airport(iata)
    return None
