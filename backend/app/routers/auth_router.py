from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user
from app.schemas.auth_schema import Token, UserCreate, UserLogin, UserRead
from app.services.auth_service import login_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate):
    try:
        user = register_user(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin):
    try:
        token = login_user(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
def me(user=Depends(get_current_user)):
    return user
