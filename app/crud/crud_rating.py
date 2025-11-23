from sqlalchemy.orm import Session
from app.db.models import AppRating
from app.schemas.schemas import AppRatingCreate


def create_rating(db: Session, user_id: int, rating_data: AppRatingCreate) -> AppRating:
    db_rating = AppRating(
        user_id=user_id, rating=rating_data.rating, comment=rating_data.comment
    )
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating


def get_user_rating(db: Session, user_id: int) -> AppRating | None:
    return db.query(AppRating).filter(AppRating.user_id == user_id).first()
