# api/endpoints/pressures.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.schemas import BPCreate, BPOut, BPList
from app.crud.crud_pressure import create_for_user, get_last, get_list, delete_one
import time
import logging

logger = logging.getLogger("pressures_endpoint")

router = APIRouter(prefix="/pressures", tags=["pressures"])


@router.post("", response_model=BPOut)
def create_pressure(
    data: BPCreate, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    pressure = create_for_user(db, user.id, data)
    logger.info(
        "Presión registrada: usuario=%s, sistólica=%s, diastólica=%s",
        user.id,
        pressure.systolic,
        pressure.diastolic,
    )
    return pressure


@router.get("", response_model=BPList)
def list_pressures(
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(5, ge=1, le=100, description="Registros por página"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    start_time = time.time()
    skip = (page - 1) * limit
    items, total = get_list(db, user.id, skip, limit)
    elapsed = (time.time() - start_time) * 1000  # ms
    logger.info(
        "Historial consultado: usuario=%s | Página=%s | Registros=%s | Tiempo: %.2f ms | Path: /api/v1/pressures",
        user.id,
        page,
        len(items),
        elapsed,
    )
    return {"items": items, "total": total, "page": page, "limit": limit}


@router.get("/last", response_model=BPOut | None)
def last_pressure(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return get_last(db, user.id)


@router.delete("/{bp_id}", status_code=204)
def remove_pressure(
    bp_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    ok = delete_one(db, user.id, bp_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
