import logging

logger = logging.getLogger("ratings_endpoint")

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.db.models import User
from app.schemas.schemas import AppRatingCreate, AppRatingResponse
from app.crud import crud_rating

# El prefijo "/ratings" se aplicará a todas las rutas de este router
router = APIRouter(prefix="/ratings", tags=["ratings"])


# ✅ CORRECCIÓN: La ruta ahora es "/" porque el prefijo ya es "/ratings"
@router.post("/", response_model=AppRatingResponse, status_code=status.HTTP_201_CREATED)
def create_app_rating(
    rating_data: AppRatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crear valoración de la aplicación"""
    existing = crud_rating.get_user_rating(db, current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya has valorado la aplicación",
        )

    rating = crud_rating.create_rating(db, current_user.id, rating_data)
    logger.info(
        "Valoración registrada: usuario=%s, rating=%s",
        current_user.id,
        rating_data.rating,
    )
    return rating


# ✅ CORRECCIÓN: La ruta ahora es "/me" porque el prefijo ya es "/ratings"
@router.get("/me", response_model=AppRatingResponse | None)
def get_my_rating(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Obtener mi valoración"""
    return crud_rating.get_user_rating(db, current_user.id)
