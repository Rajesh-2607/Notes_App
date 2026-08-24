import httpx

from app.config import settings
from app.schemas.auth_schema import UserCreate, UserLogin

AUTH_BASE = f"{settings.SUPABASE_URL}/auth/v1"


def _headers() -> dict:
    return {"apikey": settings.SUPABASE_ANON_KEY, "Content-Type": "application/json"}


def _extract_error(data: dict, fallback: str) -> str:
    return data.get("error_description") or data.get("msg") or data.get("message") or fallback


def register_user(payload: UserCreate) -> dict:
    response = httpx.post(
        f"{AUTH_BASE}/signup",
        json={"email": str(payload.email), "password": payload.password},
        headers=_headers(),
        timeout=10,
    )
    data = response.json()
    if response.status_code >= 400:
        raise ValueError(_extract_error(data, "Registration failed"))

    user = data.get("user") or data
    return {"id": user["id"], "email": user["email"]}


def login_user(payload: UserLogin) -> str:
    response = httpx.post(
        f"{AUTH_BASE}/token",
        params={"grant_type": "password"},
        json={"email": str(payload.email), "password": payload.password},
        headers=_headers(),
        timeout=10,
    )
    data = response.json()
    if response.status_code >= 400:
        raise ValueError(_extract_error(data, "Invalid email or password"))

    return data["access_token"]
