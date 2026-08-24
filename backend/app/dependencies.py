from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from app.config import settings

security = HTTPBearer()

_jwk_client: PyJWKClient | None = None


@dataclass
class SupabaseUser:
    id: str
    email: str | None


def _get_jwk_client() -> PyJWKClient:
    global _jwk_client
    if _jwk_client is None:
        _jwk_client = PyJWKClient(
            f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json",
            cache_keys=True,
            lifespan=600,
        )
    return _jwk_client


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> SupabaseUser:
    token = credentials.credentials
    try:
        signing_key = _get_jwk_client().get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256"],
            audience="authenticated",
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials") from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return SupabaseUser(id=user_id, email=payload.get("email"))
