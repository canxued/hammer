from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Event
from ..schemas import EventIn, EventOut

router = APIRouter()

@router.post("/events", response_model=EventOut)
async def ingest_event(event: EventIn, db: Session = Depends(get_db)):
    db_event = Event(
        source=event.source,
        event_time=event.event_time,
        src_ip=event.src_ip,
        dst_ip=event.dst_ip,
        hostname=event.hostname,
        username=event.username,
        process_name=event.process_name,
        event_type=event.event_type,
        raw=event.raw,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@router.post("/bulk/events", response_model=List[EventOut])
async def ingest_events_bulk(events: List[EventIn], db: Session = Depends(get_db)):
    db_events: List[Event] = []
    for event in events:
        db_events.append(
            Event(
                source=event.source,
                event_time=event.event_time,
                src_ip=event.src_ip,
                dst_ip=event.dst_ip,
                hostname=event.hostname,
                username=event.username,
                process_name=event.process_name,
                event_type=event.event_type,
                raw=event.raw,
            )
        )
    db.add_all(db_events)
    db.commit()
    for e in db_events:
        db.refresh(e)
    return db_events
