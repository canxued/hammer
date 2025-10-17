from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..db import get_db
from ..models import Event, Alert
from ..schemas import EventOut, AlertOut

router = APIRouter()

@router.get("/events", response_model=List[EventOut])
async def search_events(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="search text in hostname, username, process_name, type"),
    src_ip: Optional[str] = None,
    dst_ip: Optional[str] = None,
    limit: int = 100,
):
    stmt = select(Event)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            (Event.hostname.ilike(like))
            | (Event.username.ilike(like))
            | (Event.process_name.ilike(like))
            | (Event.event_type.ilike(like))
        )
    if src_ip:
        stmt = stmt.where(Event.src_ip == src_ip)
    if dst_ip:
        stmt = stmt.where(Event.dst_ip == dst_ip)
    stmt = stmt.order_by(Event.event_time.desc()).limit(limit)
    return list(db.scalars(stmt))

@router.get("/alerts", response_model=List[AlertOut])
async def list_alerts(db: Session = Depends(get_db), severity: Optional[str] = None, limit: int = 100):
    stmt = select(Alert)
    if severity:
        stmt = stmt.where(Alert.severity == severity)
    stmt = stmt.order_by(Alert.created_at.desc()).limit(limit)
    return list(db.scalars(stmt))
