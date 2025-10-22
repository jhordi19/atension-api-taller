# crud/crud_evaluation.py
from sqlalchemy.orm import Session
from app.db import models
from app.schemas import schemas
from enum import Enum

def _enum_to_value_dict(d: dict):
    cleaned = {}
    for k,v in d.items():
        if isinstance(v, Enum):
            cleaned[k] = v.value
        else:
            cleaned[k] = v
    return cleaned

def create_evaluation(
    db: Session,
    user_id: int,
    evaluation_in: schemas.EvaluationCreate,
    probability: float,
    risk_level: str,
    imc: float,
    age: int
):
    data = _enum_to_value_dict(evaluation_in.model_dump())
    obj = models.Evaluation(
        user_id=user_id,
        imc=imc,
        age=age,
        probability=probability,
        risk_level=risk_level,
        **data
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_user_evaluations(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """
    Obtiene una lista de todas las evaluaciones para un usuario específico.
    """
    return (
        db.query(models.Evaluation)
        .filter(models.Evaluation.user_id == user_id)
        .order_by(models.Evaluation.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_evaluations_by_user(db: Session, user_id: int):
    return db.query(models.Evaluation)\
        .filter(models.Evaluation.user_id == user_id)\
        .order_by(models.Evaluation.created_at.desc())\
        .all()