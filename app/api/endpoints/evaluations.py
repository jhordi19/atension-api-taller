# api/endpoints/evaluations.py (ACTUALIZADO Y CORREGIDO)
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from ...db import base as db_base, models
from ...schemas import schemas
from ...crud import crud_evaluation
from ...ml.predictor import predictor
from ..deps import get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.EvaluationResponse, status_code=status.HTTP_201_CREATED)
def create_new_evaluation(
    evaluation_in: schemas.EvaluationCreate,
    db: Session = Depends(db_base.get_db),
    current_user: models.User = Depends(get_current_user)
):
    user_data = {
        "birth_date": current_user.birth_date,
        "gender": current_user.gender
    }

    probability, risk_level, imc, age = predictor.predict(
        user_data=user_data,
        evaluation_data=evaluation_in   # ← antes era evaluation_in.dict()
    )

    db_evaluation = crud_evaluation.create_evaluation(
        db=db,
        user_id=current_user.id,
        evaluation_in=evaluation_in,
        probability=probability,
        risk_level=risk_level,
        imc=imc,
        age=age
    )
    return db_evaluation

@router.get("/", response_model=List[schemas.EvaluationResponse])
def read_user_evaluations(
    db: Session = Depends(db_base.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Obtiene el historial de evaluaciones del usuario autenticado.
    """
    evaluations = crud_evaluation.get_evaluations_by_user(
        db, user_id=current_user.id
    )
    return evaluations