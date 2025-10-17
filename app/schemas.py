from __future__ import annotations
from datetime import datetime
from typing import Any, List, Literal, Optional
from pydantic import BaseModel, Field

class EventIn(BaseModel):
    source: str = Field(..., description="event source name")
    event_time: datetime
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    hostname: Optional[str] = None
    username: Optional[str] = None
    process_name: Optional[str] = None
    event_type: Optional[str] = None
    raw: dict

class EventOut(EventIn):
    id: int
    received_time: datetime

    class Config:
        from_attributes = True

class AlertOut(BaseModel):
    id: int
    created_at: datetime
    severity: Literal["low","medium","high","critical"]
    title: str
    rule_name: Optional[str] = None
    indicator_value: Optional[str] = None
    event_id: Optional[int] = None
    details: Optional[dict] = None

    class Config:
        from_attributes = True

class RuleOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    severity: str
    tags: Optional[List[str]] = None
    enabled: int
    version: Optional[str] = None

    class Config:
        from_attributes = True

class IntelIn(BaseModel):
    type: Literal["ip","domain","url","hash"]
    value: str
    threat_type: Optional[str] = None
    severity: Literal["low","medium","high","critical"] = "medium"
    source: Optional[str] = None

class IntelOut(IntelIn):
    id: int

    class Config:
        from_attributes = True
