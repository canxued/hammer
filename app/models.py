from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from .db import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(64), index=True)  # e.g., suricata, sysmon, generic
    event_time = Column(DateTime, index=True, nullable=False)
    received_time = Column(DateTime, index=True, default=datetime.utcnow)
    src_ip = Column(String(64), index=True, nullable=True)
    dst_ip = Column(String(64), index=True, nullable=True)
    hostname = Column(String(255), index=True, nullable=True)
    username = Column(String(255), index=True, nullable=True)
    process_name = Column(String(255), index=True, nullable=True)
    event_type = Column(String(128), index=True, nullable=True)
    raw = Column(JSON, nullable=False)

    alerts = relationship("Alert", back_populates="event")

Index("ix_events_time_src", Event.event_time, Event.src_ip)
Index("ix_events_time_dst", Event.event_time, Event.dst_ip)

class DetectionRule(Base):
    __tablename__ = "detection_rules"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(16), default="medium")
    author = Column(String(255), nullable=True)
    tags = Column(JSON, nullable=True)
    conditions = Column(JSON, nullable=False)  # normalized rule structure
    enabled = Column(Integer, default=1)
    version = Column(String(32), nullable=True)

class ThreatIntelIndicator(Base):
    __tablename__ = "threat_intel_indicators"

    id = Column(Integer, primary_key=True)
    type = Column(String(32), index=True)  # ip, domain, url, hash
    value = Column(String(512), index=True, unique=True)
    threat_type = Column(String(128), nullable=True)
    severity = Column(String(16), default="medium")
    source = Column(String(128), nullable=True)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    severity = Column(String(16), index=True)
    title = Column(String(255), index=True)
    rule_name = Column(String(255), index=True, nullable=True)
    indicator_value = Column(String(512), nullable=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    details = Column(JSON, nullable=True)

    event = relationship("Event", back_populates="alerts")

Index("ix_alerts_rule_time", Alert.rule_name, Alert.created_at)
