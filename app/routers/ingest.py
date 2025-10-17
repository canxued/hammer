from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from ..db import get_db, SessionLocal
from ..models import Event
from ..schemas import EventIn, EventOut
from ..parsers import normalize_event_fields
from ..detection.engine import process_event_rules
from ..intel.matcher import match_event_intel

router = APIRouter()

def _analyze_event_background(event_id: int) -> None:
    db = SessionLocal()
    try:
        event = db.get(Event, event_id)
        if not event:
            return
        # Run rule engine and intel matching
        process_event_rules(db, event)
        match_event_intel(db, event)
    finally:
        db.close()


@router.post("/events", response_model=EventOut)
async def ingest_event(event: EventIn, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Normalize fields from raw content if missing
    norm = normalize_event_fields(event.source, event.raw)
    db_event = Event(
        source=event.source,
        event_time=event.event_time,
        src_ip=event.src_ip or norm.get("src_ip"),
        dst_ip=event.dst_ip or norm.get("dst_ip"),
        hostname=event.hostname or norm.get("hostname"),
        username=event.username or norm.get("username"),
        process_name=event.process_name or norm.get("process_name"),
        event_type=event.event_type or norm.get("event_type"),
        raw=event.raw,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    # Post-commit analysis in background
    background_tasks.add_task(_analyze_event_background, db_event.id)
    return db_event

@router.post("/bulk/events", response_model=List[EventOut])
async def ingest_events_bulk(events: List[EventIn], background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_events: List[Event] = []
    for event in events:
        norm = normalize_event_fields(event.source, event.raw)
        db_events.append(
            Event(
                source=event.source,
                event_time=event.event_time,
                src_ip=event.src_ip or norm.get("src_ip"),
                dst_ip=event.dst_ip or norm.get("dst_ip"),
                hostname=event.hostname or norm.get("hostname"),
                username=event.username or norm.get("username"),
                process_name=event.process_name or norm.get("process_name"),
                event_type=event.event_type or norm.get("event_type"),
                raw=event.raw,
            )
        )
    db.add_all(db_events)
    db.commit()
    for e in db_events:
        db.refresh(e)
        background_tasks.add_task(_analyze_event_background, e.id)
    return db_events
