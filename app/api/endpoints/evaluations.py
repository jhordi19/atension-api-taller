import time
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ...db import base as db_base, models
from ...schemas import schemas
from ...crud import crud_evaluation
from ...ml.predictor import predictor
from ..deps import get_current_user

# Asegura el prefijo del módulo
router = APIRouter(prefix="/evaluations", tags=["evaluations"])

# Logger dedicado solo para el endpoint de riesgo
risk_logger = logging.getLogger("risk_endpoint")
risk_logger.propagate = False
if not risk_logger.handlers:
    handler = logging.FileHandler("risk_endpoint.log", mode="a", encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s %(message)s")
    handler.setFormatter(formatter)
    risk_logger.addHandler(handler)
risk_logger.setLevel(logging.INFO)

def _bmi_category_from_imc(imc: Optional[float]) -> str:
    if imc is None:
        return "Desconocido"
    try:
        v = float(imc)
    except Exception:
        return "Desconocido"
    if v < 18.5:
        return "Bajo peso"
    if v < 25:
        return "Normal"
    if v < 30:
        return "Sobrepeso"
    return "Obesidad"

@router.post("/", response_model=schemas.EvaluationResponse, status_code=status.HTTP_201_CREATED)
def create_new_evaluation(
    evaluation_in: schemas.EvaluationCreate,
    db: Session = Depends(db_base.get_db),
    current_user: models.User = Depends(get_current_user)
):
    start_time = time.time()

    user_data = {
        "birth_date": current_user.birth_date,
        "gender": current_user.gender
    }

    probability, risk_level, imc, age = predictor.predict(
        user_data=user_data,
        evaluation_data=evaluation_in
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

    process_time = (time.time() - start_time) * 1000  # tiempo en ms

    risk_logger.info(
        f"Evaluación creada | Tiempo: {process_time:.2f} ms | Usuario: {current_user.id} | Path: /api/v1/evaluations/"
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

@router.get("/me", response_model=schemas.ProfileSummary)
def read_my_latest_evaluation(
    db: Session = Depends(db_base.get_db),
    current_user: models.User = Depends(get_current_user),
):
    evaluation = crud_evaluation.get_last_evaluation_by_user(db, user_id=current_user.id)
    if not evaluation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No evaluation found")

    days_until_next = crud_evaluation.days_until_next_evaluation(evaluation)

    # Datos base
    bmi = getattr(evaluation, "imc", None)
    bmi_category = _bmi_category_from_imc(bmi)
    gender = getattr(current_user, "gender", "Desconocido")

    # Construcción segura de factores (solo si existen los campos)
    risk_factors = []
    factor_id = 1

    # Factor por IMC
    if bmi is not None and bmi_category not in ["Normal", "Bajo peso"]:
        level = "obesity" if bmi_category == "Obesidad" else "moderate"
        risk_factors.append({
            "id": factor_id,
            "title": f"IMC {float(bmi):.1f}",
            "description": f"Tu índice de masa corporal indica {bmi_category}.",
            "recommendations": [
                "Consulta con un nutricionista",
                "Establece metas de peso realistas",
                "Incrementa actividad física gradualmente",
            ],
            "level": level,
            "icon_key": "bmi",
        })
        factor_id += 1

    # Tabaquismo (si existe el campo)
    smoking = getattr(evaluation, "smoking", None)
    if isinstance(smoking, str) and smoking and smoking.lower() != "nunca":
        level = "high" if smoking.lower() == "diario" else "moderate"
        risk_factors.append({
            "id": factor_id,
            "title": f"Fuma {smoking.lower()}",
            "description": "El tabaquismo incrementa la rigidez arterial y acelera la hipertensión.",
            "recommendations": [
                "Reduce progresivamente el número de cigarrillos",
                "Busca apoyo médico o psicológico",
                "Evita fumar dentro del hogar",
            ],
            "level": level,
            "icon_key": "smoking",
        })
        factor_id += 1

    # Actividad física (si existe)
    physical_activity = getattr(evaluation, "physical_activity", None)
    if isinstance(physical_activity, str) and physical_activity.lower() in ["nunca", "rara vez"]:
        risk_factors.append({
            "id": factor_id,
            "title": "Sedentarismo",
            "description": "La falta de actividad física aumenta el riesgo cardiovascular.",
            "recommendations": [
                "Camina al menos 30 minutos al día",
                "Usa escaleras en lugar de ascensor",
                "Realiza pausas activas cada hora",
            ],
            "level": "high",
            "icon_key": "sedentary",
        })
        factor_id += 1

    # Alcohol (si existe)
    alcohol = getattr(evaluation, "alcohol_consumption", None)
    if isinstance(alcohol, str) and alcohol.lower() not in ["nunca", "ocasionalmente"]:
        risk_factors.append({
            "id": factor_id,
            "title": "Consumo de alcohol",
            "description": "El consumo frecuente de alcohol eleva la presión arterial.",
            "recommendations": [
                "Limita el consumo a ocasiones especiales",
                "Alterna bebidas alcohólicas con agua",
                "Busca ayuda si sientes dependencia",
            ],
            "level": "moderate",
            "icon_key": "alcohol",
        })

    return {
        "age": getattr(evaluation, "age", None),
        "gender": gender,
        "bmi": bmi,
        "bmi_category": bmi_category,
        "risk_factors": risk_factors,
        "days_until_next": days_until_next,
    }