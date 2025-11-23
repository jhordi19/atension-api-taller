# api/endpoints/auth.py


from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from db.base import get_db
from schemas import schemas
from crud import crud_user
from core import security
from api.deps import get_current_user
from db import models
from core.security import generate_tokens
import logging
import time

logger = logging.getLogger("auth_endpoint")

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    start_time = time.time()
    user = crud_user.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(
        form_data.password, user.hashed_password
    ):
        elapsed = (time.time() - start_time) * 1000
        logger.warning(
            "Login fallido: usuario=%s | Tiempo: %.2f ms | Path: /api/v1/auth/token",
            form_data.username,
            elapsed,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token, refresh_token = generate_tokens(user.email)
    elapsed = (time.time() - start_time) * 1000
    logger.info(
        "Login exitoso: usuario=%s | Tiempo: %.2f ms | Path: /api/v1/auth/token",
        user.email,
        elapsed,
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=schemas.UserResponse)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user
