# db/models.py
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Enum as SAEnum, func
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
from app.core.bp_logic import BPCategory
from sqlalchemy import Enum as PgEnum

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    birth_date = Column(String)
    gender = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    evaluations = relationship("Evaluation", back_populates="user", cascade="all,delete-orphan")

class Evaluation(Base):
    __tablename__ = "evaluations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    weight_kg = Column(Float, nullable=False)
    height_cm = Column(Float, nullable=False)
    imc = Column(Float, nullable=False)
    age = Column(Integer, nullable=False)
    probability = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    reduces_salt_intake = Column(Boolean)
    alcohol_in_last_30_days = Column(Boolean)
    smoking_habit = Column(String)
    e_cigarette_use = Column(String)
    stress_days_last_month = Column(Integer)
    daily_physical_activity = Column(Boolean)
    has_high_cholesterol = Column(Boolean)
    diabetes_diagnosis = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="evaluations")

class BloodPressure(Base):
    __tablename__ = "blood_pressures"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    systolic = Column(Integer, nullable=False)
    diastolic = Column(Integer, nullable=False)
    taken_at = Column(DateTime(timezone=True), nullable=False)
    category = Column(PgEnum(BPCategory, name="bp_category"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", backref="blood_pressures")