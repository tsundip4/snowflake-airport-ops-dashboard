from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.deps import get_current_user
from app.models.flight import FlightCreate, FlightList, FlightOut, FlightUpdate
from app.services.flight_service import (
    create_flight,
    delete_flight,
    get_flight,
    list_flights,
    update_flight,
)

router = APIRouter(prefix="/flights", tags=["flights"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=FlightOut, status_code=status.HTTP_201_CREATED)
async def create(payload: FlightCreate):
    return create_flight(payload)


@router.get("/{flight_nk}", response_model=FlightOut)
async def get_one(flight_nk: str):
    row = get_flight(flight_nk)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flight not found")
    return row


@router.get("", response_model=FlightList)
async def list_all(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    dep_iata: str | None = None,
    arr_iata: str | None = None,
    flight_date: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
):
    rows, total = list_flights(limit, offset, dep_iata, arr_iata, flight_date, status_filter)
    return FlightList(items=rows, total=total, limit=limit, offset=offset)


@router.put("/{flight_nk}", response_model=FlightOut)
async def update(flight_nk: str, payload: FlightUpdate):
    row = update_flight(flight_nk, payload)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flight not found")
    return row


@router.delete("/{flight_nk}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(flight_nk: str):
    delete_flight(flight_nk)
    return None
