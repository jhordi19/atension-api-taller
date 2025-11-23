# ml/predictor.py (ACTUALIZADO Y CORREGIDO)
import joblib
import numpy as np
from datetime import date, datetime
import os
from typing import Any, Union

try:
    from ..schemas.schemas import EvaluationCreate  # opcional para type hints
except ImportError:
    EvaluationCreate = Any  # fallback


class HypertensionPredictor:
    def __init__(self, model_path: str):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelo no encontrado: {model_path}")
        self.model = joblib.load(model_path)
        self.feature_order = [
            "Age",
            "Sex",
            "BMI",
            "Salt",
            "PhysActivity",
            "Smoker",
            "MentHlth",
            "Alcohol",
            "Vaper",
            "Diabetes",
            "HighChol",
        ]

    # -------------------- Utilidades --------------------
    def _to_date(self, birth_date: Union[str, date]) -> date:
        if isinstance(birth_date, date):
            return birth_date
        # Intenta varios formatos
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(birth_date, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Formato de fecha no soportado: {birth_date}")

    def _calculate_age(self, birth_date: Union[str, date]) -> int:
        bd = self._to_date(birth_date)
        today = date.today()
        return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))

    def _map_age_to_group(self, age: int) -> int:
        bins = [
            (18, 24),
            (25, 29),
            (30, 34),
            (35, 39),
            (40, 44),
            (45, 49),
            (50, 54),
            (55, 59),
            (60, 64),
            (65, 69),
            (70, 74),
            (75, 79),
        ]
        for idx, (a, b) in enumerate(bins, start=1):
            if a <= age <= b:
                return idx
        return 13  # 80+

    def _calculate_bmi(self, weight_kg: float, height_cm: float) -> float:
        if not height_cm:
            raise ValueError("height_cm no puede ser 0")
        return round(weight_kg / ((height_cm / 100) ** 2), 2)

    def _get(self, obj, name: str):
        if isinstance(obj, dict):
            return obj[name]
        return getattr(obj, name)

    # -------------------- Normalización de categorías --------------------
    def _normalize_smoker(self, value: Any) -> int:
        if hasattr(value, "value"):
            value = value.value
        value = str(value).strip().lower()
        mapping = {
            "fumo a diario": 1,
            "diario": 1,
            "daily": 1,
            "fumo ocasionalmente": 2,
            "ocasional": 2,
            "occasionally": 2,
            "exfumador": 3,
            "ex-smoker": 3,
            "former": 3,
            "no fumo": 4,
            "none": 4,
            "nunca": 4,
            "never": 4,
        }
        return mapping.get(value, 4)

    def _normalize_vaper(self, value: Any) -> int:
        if hasattr(value, "value"):
            value = value.value
        value = str(value).strip().lower()
        mapping = {
            "diariamente": 1,
            "daily": 1,
            "ocasionalmente": 2,
            "occasionally": 2,
            "rara vez": 3,
            "rarely": 3,
            "nunca he usado": 4,
            "nunca": 4,
            "never": 4,
        }
        return mapping.get(value, 4)

    def _normalize_diabetes(self, value: Any) -> int:
        if hasattr(value, "value"):
            value = value.value
        value = str(value).strip().lower()
        return 1 if value in {"si", "sí", "yes", "type1", "type2"} else 0

    def _normalize_gender(self, gender: str) -> int:
        g = str(gender).strip().lower()
        return 1 if g in {"hombre", "male", "m"} else 0  # 1=Hombre, 0=Mujer

    # -------------------- Construcción de features --------------------
    def _map_inputs_to_model_features(
        self, age_group: int, gender: str, evaluation_data: Any
    ) -> dict:
        weight = self._get(evaluation_data, "weight_kg")
        height = self._get(evaluation_data, "height_cm")
        bmi = self._calculate_bmi(weight, height)
        return {
            "Age": age_group,
            "Sex": self._normalize_gender(gender),
            "BMI": round(bmi),
            "Salt": 1 if self._get(evaluation_data, "reduces_salt_intake") else 0,
            "PhysActivity": (
                1 if self._get(evaluation_data, "daily_physical_activity") else 0
            ),
            "Smoker": self._normalize_smoker(
                self._get(evaluation_data, "smoking_habit")
            ),
            "MentHlth": self._get(evaluation_data, "stress_days_last_month"),
            "Alcohol": (
                1 if self._get(evaluation_data, "alcohol_in_last_30_days") else 0
            ),
            "Vaper": self._normalize_vaper(
                self._get(evaluation_data, "e_cigarette_use")
            ),
            "Diabetes": self._normalize_diabetes(
                self._get(evaluation_data, "diabetes_diagnosis")
            ),
            "HighChol": 1 if self._get(evaluation_data, "has_high_cholesterol") else 0,
        }, bmi

    # -------------------- Predicción --------------------
    def predict(self, user_data: dict, evaluation_data: Any):
        age_real = self._calculate_age(user_data["birth_date"])
        age_group = self._map_age_to_group(age_real)
        features_dict, bmi = self._map_inputs_to_model_features(
            age_group, user_data["gender"], evaluation_data
        )

        # Ordenar vector
        input_vector = np.array(
            [features_dict[name] for name in self.feature_order], dtype=float
        ).reshape(1, -1)

        proba = float(self.model.predict_proba(input_vector)[0][1])

        if proba < 0.30:
            risk_level = "Bajo"
        elif proba < 0.60:
            risk_level = "Moderado"
        else:
            risk_level = "Alto"

        # Devuelve la tupla esperada por el endpoint
        return proba, risk_level, bmi, age_real


# Inicialización
model_file_path = os.path.join(
    os.path.dirname(__file__), "models", "modelo_rf_actualizado.pkl"
)
predictor = HypertensionPredictor(model_path=model_file_path)
