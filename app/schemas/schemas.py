# schemas/schemas.py (ACTUALIZADO Y CORREGIDO)
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional
from datetime import date, datetime
from enum import Enum
from core.bp_logic import BPCategory  # <- ADD

# --- Clases Enum para validación estricta de entradas ---
class SmokingHabit(str, Enum):
    fuma_diario = "Fumo a diario"
    fuma_ocasionalmente = "Fumo ocasionalmente"
    exfumador = "Exfumador"
    no_fuma = "No Fumo"

class ECigaretteUse(str, Enum):
    diariamente = "Diariamente"
    ocasionalmente = "Ocasionalmente"
    rara_vez = "Rara vez"
    nunca_he_usado = "Nunca he usado"

class DiabetesDiagnosis(str, Enum):
    si = "Si"
    no = "No"
    prediabetes = "Prediabetes"

# --- Esquemas para Usuarios (Sin cambios) ---
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    birth_date: date
    gender: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# --- Esquemas para Evaluaciones (CORREGIDOS) ---
class EvaluationCreate(BaseModel):
    """Esquema para los datos que el frontend envía para crear una evaluación."""
    weight_kg: float = Field(..., gt=0, description="Peso en kilogramos")
    height_cm: float = Field(..., gt=0, description="Altura en centímetros")
    reduces_salt_intake: bool
    alcohol_in_last_30_days: bool
    smoking_habit: SmokingHabit
    e_cigarette_use: ECigaretteUse
    stress_days_last_month: int = Field(..., ge=0, le=30)
    daily_physical_activity: bool
    has_high_cholesterol: bool
    diabetes_diagnosis: DiabetesDiagnosis

class EvaluationResponse(BaseModel):
    id: int
    user_id: int
    weight_kg: float
    height_cm: float
    imc: float
    age: int
    probability: float
    risk_level: str
    reduces_salt_intake: bool
    alcohol_in_last_30_days: bool
    smoking_habit: SmokingHabit
    e_cigarette_use: ECigaretteUse
    stress_days_last_month: int
    daily_physical_activity: bool
    has_high_cholesterol: bool
    diabetes_diagnosis: DiabetesDiagnosis
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EvaluationHistoryResponse(EvaluationResponse):
    """Esquema para devolver los detalles del historial."""
    pass


# --- Esquemas para Autenticación (Sin cambios) ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Esquemas para Presión Arterial (CORREGIDOS) ---
class BPBase(BaseModel):
    systolic: int = Field(..., ge=50, le=260)
    diastolic: int = Field(..., ge=30, le=180)
    taken_at: datetime

class BPCreate(BPBase):
    pass

class BPOut(BPBase):
    id: int
    category: BPCategory
    model_config = ConfigDict(from_attributes=True)

class BPList(BaseModel):
    items: list[BPOut]
    total: int

# --- Esquemas para Factores de Riesgo (CORREGIDOS) ---
class RiskFactorBase(BaseModel):
    id: int
    title: str
    description: str
    recommendations: List[str]
    level: str
    icon_key: str

    class Config:
        orm_mode = True

class ProfileSummary(BaseModel):
    age: int
    gender: str
    bmi: float
    bmi_category: str
    risk_factors: List[RiskFactorBase]
    days_until_next: int