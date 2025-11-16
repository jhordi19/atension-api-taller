# api/endpoints/evaluations.py
import time
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from db.base import get_db
from db import models
from schemas import schemas
from crud import crud_evaluation
from ml.predictor import predictor
from api.deps import get_current_user

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
    db: Session = Depends(get_db),
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
    db: Session = Depends(get_db),
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
    db: Session = Depends(get_db),
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

    # Construcción completa de factores de riesgo
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

    # Tabaquismo
    smoking_habit = getattr(evaluation, "smoking_habit", None)
    if smoking_habit and smoking_habit not in ["No Fumo", "Exfumador"]:
        level = "high" if smoking_habit == "Fumo a diario" else "moderate"
        risk_factors.append({
            "id": factor_id,
            "title": "Tabaquismo",
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

    # Actividad física
    daily_physical_activity = getattr(evaluation, "daily_physical_activity", None)
    if daily_physical_activity is False:
        risk_factors.append({
            "id": factor_id,
            "title": "Sedentarismo",
            "description": "La falta de actividad física aumenta el riesgo cardiovascular.",
            "recommendations": [
                "Camina al menos 30 minutos al día",
                "Usa escaleras en lugar de ascensor",
                "Realiza pausas activas cada hora",
            ],
            "level": "moderate",
            "icon_key": "sedentary",
        })
        factor_id += 1

    # Colesterol alto
    has_high_cholesterol = getattr(evaluation, "has_high_cholesterol", None)
    if has_high_cholesterol is True:
        risk_factors.append({
            "id": factor_id,
            "title": "Colesterol Alto",
            "description": "El colesterol alto es un factor de riesgo importante para hipertensión.",
            "recommendations": [
                "Reduce el consumo de grasas saturadas",
                "Aumenta el consumo de fibra",
                "Considera medicación si el médico lo indica",
            ],
            "level": "high",
            "icon_key": "cholesterol",
        })
        factor_id += 1

    # Diabetes
    diabetes_diagnosis = getattr(evaluation, "diabetes_diagnosis", None)
    if diabetes_diagnosis and diabetes_diagnosis != "No":
        level = "high" if diabetes_diagnosis == "Si" else "moderate"
        risk_factors.append({
            "id": factor_id,
            "title": "Diabetes",
            "description": "La diabetes aumenta significativamente el riesgo de hipertensión.",
            "recommendations": [
                "Controla tus niveles de glucosa regularmente",
                "Sigue el tratamiento médico indicado",
                "Mantén una dieta balanceada",
            ],
            "level": level,
            "icon_key": "diabetes",
        })
        factor_id += 1

    # Consumo de alcohol
    alcohol_in_last_30_days = getattr(evaluation, "alcohol_in_last_30_days", None)
    if alcohol_in_last_30_days is True:
        risk_factors.append({
            "id": factor_id,
            "title": "Consumo de Alcohol",
            "description": "El consumo de alcohol puede elevar la presión arterial.",
            "recommendations": [
                "Limita el consumo a ocasiones especiales",
                "Alterna bebidas alcohólicas con agua",
                "No excedas 2 bebidas por día",
            ],
            "level": "moderate",
            "icon_key": "alcohol",
        })
        factor_id += 1

    # Consumo de sal
    reduces_salt_intake = getattr(evaluation, "reduces_salt_intake", None)
    if reduces_salt_intake is False:
        risk_factors.append({
            "id": factor_id,
            "title": "Alto Consumo de Sal",
            "description": "El exceso de sal es un factor clave en el desarrollo de hipertensión.",
            "recommendations": [
                "Reduce el consumo de alimentos procesados",
                "Cocina sin sal agregada",
                "Lee las etiquetas nutricionales",
            ],
            "level": "moderate",
            "icon_key": "salt",
        })
        factor_id += 1

    # Estrés
    stress_days_last_month = getattr(evaluation, "stress_days_last_month", None)
    if stress_days_last_month and stress_days_last_month > 15:
        risk_factors.append({
            "id": factor_id,
            "title": "Estrés Crónico",
            "description": f"Has experimentado estrés {stress_days_last_month} días en el último mes.",
            "recommendations": [
                "Practica técnicas de relajación",
                "Considera meditación o yoga",
                "Busca apoyo profesional si es necesario",
            ],
            "level": "moderate",
            "icon_key": "stress",
        })
        factor_id += 1

    # Cigarrillo electrónico
    e_cigarette_use = getattr(evaluation, "e_cigarette_use", None)
    if e_cigarette_use and e_cigarette_use not in ["Nunca he usado", "Rara vez"]:
        level = "high" if e_cigarette_use == "Diariamente" else "moderate"
        risk_factors.append({
            "id": factor_id,
            "title": "Cigarrillo Electrónico",
            "description": "El uso de cigarrillos electrónicos también afecta la salud cardiovascular.",
            "recommendations": [
                "Considera dejar gradualmente",
                "Busca alternativas más saludables",
                "Consulta con un especialista",
            ],
            "level": level,
            "icon_key": "vaping",
        })

    return {
        "age": getattr(evaluation, "age", None),
        "gender": gender,
        "bmi": bmi,
        "bmi_category": bmi_category,
        "risk_factors": risk_factors,
        "days_until_next": days_until_next,
    }