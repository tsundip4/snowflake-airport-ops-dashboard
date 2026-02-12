from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.deps import get_current_user
from app.models.ai import AiAskRequest, AiAskResponse
from app.services.ai_service import ask_ai

router = APIRouter(prefix="/ai", tags=["ai"], dependencies=[Depends(get_current_user)])


@router.post("/ask", response_model=AiAskResponse)
async def ask(payload: AiAskRequest):
    try:
        answer, model = ask_ai(payload.question)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="AI provider error"
        ) from exc
    return AiAskResponse(answer=answer, model=model)
