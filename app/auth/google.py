import time
from typing import Dict, Optional

import requests
from jose import jwt

from app.config import get_settings

JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
TOKEN_URL = "https://oauth2.googleapis.com/token"
ISSUERS = {"https://accounts.google.com", "accounts.google.com"}

_JWKS_CACHE: Dict[str, object] = {"keys": None, "expires_at": 0}


def _get_jwks() -> dict:
    now = int(time.time())
    if _JWKS_CACHE["keys"] and _JWKS_CACHE["expires_at"] > now:
        return _JWKS_CACHE["keys"]  # type: ignore[return-value]

    resp = requests.get(JWKS_URL, timeout=10)
    resp.raise_for_status()
    jwks = resp.json()
    _JWKS_CACHE["keys"] = jwks
    # Cache for 1 hour
    _JWKS_CACHE["expires_at"] = now + 3600
    return jwks


def _get_google_key(kid: str) -> Optional[dict]:
    jwks = _get_jwks()
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key
    return None


def verify_google_id_token(id_token: str, access_token: Optional[str] = None) -> dict:
    settings = get_settings()
    header = jwt.get_unverified_header(id_token)
    kid = header.get("kid")
    if not kid:
        raise ValueError("Missing kid in token header")

    key = _get_google_key(kid)
    if not key:
        raise ValueError("No matching JWK for token")

    payload = jwt.decode(
        id_token,
        key,
        algorithms=["RS256"],
        audience=settings.google_client_id,
        issuer=ISSUERS,
        access_token=access_token,
        options={"verify_at_hash": access_token is not None},
    )
    return payload


def exchange_code_for_tokens(code: str) -> dict:
    settings = get_settings()
    data = {
        "code": code,
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "redirect_uri": settings.google_redirect_uri,
        "grant_type": "authorization_code",
    }
    resp = requests.post(TOKEN_URL, data=data, timeout=15)
    resp.raise_for_status()
    return resp.json()


def build_google_auth_url(state: Optional[str] = None) -> str:
    settings = get_settings()
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    if state:
        params["state"] = state
    qs = "&".join(f"{k}={requests.utils.quote(str(v))}" for k, v in params.items())
    return f"https://accounts.google.com/o/oauth2/v2/auth?{qs}"
