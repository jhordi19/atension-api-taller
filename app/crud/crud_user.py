# crud/crud_user.py
from sqlalchemy.orm import Session
from ..db import models
from ..schemas import schemas
from ..core.security import get_password_hash

def get_user_by_email(db: Session, email: str):
    """
    Busca un usuario por su dirección de correo electrónico.
    """
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    """
    Crea un nuevo usuario en la base de datos.
    """
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        birth_date=user.birth_date,
        gender=user.gender
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user