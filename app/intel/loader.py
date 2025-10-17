from __future__ import annotations
from typing import List
import glob
import os
import yaml
from sqlalchemy.orm import Session

from ..models import ThreatIntelIndicator


def load_intel_from_dir(db: Session, directory: str = "data/intel") -> List[ThreatIntelIndicator]:
    os.makedirs(directory, exist_ok=True)
    created: List[ThreatIntelIndicator] = []
    paths = sorted(glob.glob(os.path.join(directory, "*.yml")) + glob.glob(os.path.join(directory, "*.yaml")))
    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f) or {}
        items = doc.get("indicators", [])
        for it in items:
            value = it.get("value")
            type_ = it.get("type")
            if not value or not type_:
                continue
            existing = db.query(ThreatIntelIndicator).filter(ThreatIntelIndicator.value == value).first()
            if existing:
                # update minimal fields
                existing.severity = it.get("severity", existing.severity)
                existing.source = it.get("source", existing.source)
                existing.threat_type = it.get("threat_type", existing.threat_type)
            else:
                obj = ThreatIntelIndicator(
                    type=type_,
                    value=value,
                    severity=it.get("severity", "medium"),
                    source=it.get("source"),
                    threat_type=it.get("threat_type"),
                )
                db.add(obj)
                created.append(obj)
    if created:
        db.commit()
        for c in created:
            db.refresh(c)
    return created
