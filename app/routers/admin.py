from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..db import get_db
from ..models import DetectionRule, ThreatIntelIndicator
from ..schemas import IntelIn, IntelOut, RuleOut

router = APIRouter()

@router.post("/intel", response_model=IntelOut)
async def add_intel(indicator: IntelIn, db: Session = Depends(get_db)):
    obj = ThreatIntelIndicator(
        type=indicator.type,
        value=indicator.value,
        threat_type=indicator.threat_type,
        severity=indicator.severity,
        source=indicator.source,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/intel", response_model=List[IntelOut])
async def list_intel(db: Session = Depends(get_db), limit: int = 200):
    stmt = select(ThreatIntelIndicator).order_by(ThreatIntelIndicator.last_seen.desc()).limit(limit)
    return list(db.scalars(stmt))

@router.get("/rules", response_model=List[RuleOut])
async def list_rules(db: Session = Depends(get_db)):
    stmt = select(DetectionRule).order_by(DetectionRule.severity.desc())
    return list(db.scalars(stmt))
