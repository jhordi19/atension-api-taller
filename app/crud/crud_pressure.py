from sqlalchemy.orm import Session
from sqlalchemy import desc
from db.models import BloodPressure
from schemas.schemas import BPCreate
from core.bp_logic import classify_bp

def create_for_user(db: Session, user_id: int, data: BPCreate) -> BloodPressure:
    cat = classify_bp(data.systolic, data.diastolic)
    obj = BloodPressure(
        user_id=user_id,
        systolic=data.systolic,
        diastolic=data.diastolic,
        taken_at=data.taken_at,
        category=cat.value,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_last(db: Session, user_id: int):
    return (
        db.query(BloodPressure)
        .filter(BloodPressure.user_id == user_id)
        .order_by(desc(BloodPressure.taken_at))
        .first()
    )

def get_list(db: Session, user_id: int, skip: int = 0, limit: int = 50):
    q = db.query(BloodPressure).filter(BloodPressure.user_id == user_id)
    total = q.count()
    items = q.order_by(desc(BloodPressure.taken_at)).offset(skip).limit(limit).all()
    return items, total

def delete_one(db: Session, user_id: int, bp_id: int) -> bool:
    row = (
        db.query(BloodPressure)
        .filter(BloodPressure.user_id == user_id, BloodPressure.id == bp_id)
        .first()
    )
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True