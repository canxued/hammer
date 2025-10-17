from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..db import get_db
from ..models import Alert
from ..schemas import AlertOut

router = APIRouter()

@router.get("/alerts", response_model=List[AlertOut])
async def get_alerts(db: Session = Depends(get_db), limit: int = 100):
    stmt = select(Alert).order_by(Alert.created_at.desc()).limit(limit)
    return list(db.scalars(stmt))
