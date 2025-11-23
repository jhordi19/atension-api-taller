# crud/crud_evaluation.py
from sqlalchemy.orm import Session
from db import models
from schemas import schemas
from enum import Enum


def _enum_to_value_dict(d: dict):
    cleaned = {}
    for k, v in d.items():
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
    age: int,
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
    return (
        db.query(models.Evaluation)
        .filter(models.Evaluation.user_id == user_id)
        .order_by(models.Evaluation.created_at.desc())
        .all()
    )


def get_last_evaluation_by_user(db: Session, user_id: int):
    return (
        db.query(models.Evaluation)
        .filter(models.Evaluation.user_id == user_id)
        .order_by(models.Evaluation.id.desc())  # o .created_at.desc() si existe
        .first()
    )


def days_until_next_evaluation(evaluation) -> int:
    """
    Calcula días a partir de evaluation.risk_level.
    Acepta etiquetas en español/inglés y tolera "RiskLevel.alto".
    """
    label: str = (getattr(evaluation, "risk_level", "") or "").strip().lower()
    if label.startswith("risklevel."):
        label = label.split(".", 1)[1]

    mapping = {
        "bajo": 90,
        "low": 90,
        "medio": 60,
        "moderado": 60,
        "moderate": 60,
        "medium": 60,
        "alto": 30,
        "high": 30,
        "muy alto": 15,
        "muy_alto": 15,
        "very high": 15,
        "very_high": 15,
    }

    # Si llegara numérico (0=bajo,1=medio,2=alto)
    try:
        return {0: 90, 1: 60, 2: 30}[int(label)]
    except Exception:
        pass

    return mapping.get(label, 60)
