# api/endpoints/users.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db import base as db_base
from schemas import schemas
from crud import crud_user
from core import security, config

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(db_base.get_db)):
    """
    Endpoint para registrar un nuevo usuario y devolver tokens de acceso.
    """
    # Verificar si el usuario ya existe
    db_user = crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado."
        )
    
    # Crear usuario
    new_user = crud_user.create_user(db=db, user=user)
    
    # Crear tokens para login automático
    access_token_expires = timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )
    
    # Crear refresh token
    refresh_token_expires = timedelta(days=7)
    refresh_token = security.create_access_token(
        data={"sub": new_user.email}, expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }