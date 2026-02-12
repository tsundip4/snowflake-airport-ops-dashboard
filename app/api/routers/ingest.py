import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.deps import get_current_user
from app.models.ingest import IngestResponse
from app.services.ingest_service import ingest_flights

router = APIRouter(prefix="/ingest", tags=["ingest"], dependencies=[Depends(get_current_user)])
logger = logging.getLogger(__name__)


@router.post("/flights", response_model=IngestResponse)
async def ingest(
    dep_iata: str | None = Query(None, min_length=3, max_length=4),
    arr_iata: str | None = Query(None, min_length=3, max_length=4),
    limit: int = Query(50, ge=1, le=100),
):
    try:
        result = ingest_flights(dep_iata=dep_iata, arr_iata=arr_iata, limit=limit)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Ingest failed: dep_iata=%s limit=%s", dep_iata, limit)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
