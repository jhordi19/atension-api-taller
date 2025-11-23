# api/endpoints/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.base import get_db
from schemas import schemas
from crud import crud_user
from core.security import generate_tokens

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    exists = crud_user.get_user_by_email(db, email=user.email)
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado.",
        )

    new_user = crud_user.create_user(db=db, user=user)

    # ✅ Usar función auxiliar para generar tokens
    access_token, refresh_token = generate_tokens(new_user.email)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
