import logging
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse

from app.auth.jwt import create_access_token
from app.auth.google import build_google_auth_url, exchange_code_for_tokens, verify_google_id_token
from app.config import get_settings
from app.models.auth import GoogleAuthCodeRequest, LoginRequest, OAuthUrlResponse, TokenResponse
from app.services.user_service import authenticate_user, get_or_create_user_by_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    user = authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(subject=user["EMAIL"])
    return TokenResponse(access_token=token)


@router.get("/google/url", response_model=OAuthUrlResponse)
async def google_auth_url(state: str | None = None):
    settings = get_settings()
    if not settings.google_client_id or not settings.google_redirect_uri:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Google OAuth not configured"
        )
    return OAuthUrlResponse(url=build_google_auth_url(state))


@router.get("/google/callback")
async def google_callback(code: str):
    settings = get_settings()
    if (
        not settings.google_client_id
        or not settings.google_client_secret
        or not settings.google_redirect_uri
    ):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Google OAuth not configured"
        )

    tokens = exchange_code_for_tokens(code)
    id_token = tokens.get("id_token")
    if not id_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing id_token from Google"
        )

    try:
        claims = verify_google_id_token(id_token)
    except Exception as exc:
        logger.exception("Google token verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token"
        ) from exc

    if not claims.get("email_verified"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not verified")

    email = claims.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not found in token"
        )

    user = get_or_create_user_by_email(email)
    token = create_access_token(subject=user["EMAIL"])
    if settings.frontend_redirect_url:
        target = settings.frontend_redirect_url.rstrip("/") + f"/#token={token}"
        return RedirectResponse(url=target)
    return TokenResponse(access_token=token)


@router.post("/google/token", response_model=TokenResponse)
async def google_token(payload: GoogleAuthCodeRequest):
    return await google_callback(payload.code)
