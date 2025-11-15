from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.schemas import BPCreate, BPOut, BPList
from app.crud.crud_pressure import create_for_user, get_last, get_list, delete_one

router = APIRouter(prefix="/pressures", tags=["pressures"])

@router.post("", response_model=BPOut)
def create_pressure(data: BPCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return create_for_user(db, user.id, data)

@router.get("", response_model=BPList)
def list_pressures(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    items, total = get_list(db, user.id, skip, limit)
    return {"items": items, "total": total}

@router.get("/last", response_model=BPOut | None)
def last_pressure(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return get_last(db, user.id)

@router.delete("/{bp_id}", status_code=204)
def remove_pressure(bp_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ok = delete_one(db, user.id, bp_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")