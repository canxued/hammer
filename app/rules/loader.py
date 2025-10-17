from __future__ import annotations
from typing import List, Dict, Any
import glob
import os
import yaml
from sqlalchemy.orm import Session

from ..models import DetectionRule


def load_rules_from_dir(db: Session, directory: str = "data/rules") -> List[DetectionRule]:
    os.makedirs(directory, exist_ok=True)
    created_or_updated: List[DetectionRule] = []
    for path in sorted(glob.glob(os.path.join(directory, "*.yml")) + glob.glob(os.path.join(directory, "*.yaml"))):
        with open(path, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f) or {}
        name = doc.get("name")
        if not name:
            continue
        rule = db.query(DetectionRule).filter(DetectionRule.name == name).first()
        fields = {
            "name": name,
            "description": doc.get("description"),
            "severity": doc.get("severity", "medium"),
            "author": doc.get("author"),
            "tags": doc.get("tags"),
            "conditions": doc.get("condition") or doc.get("conditions") or {},
            "enabled": 1 if doc.get("enabled", True) else 0,
            "version": doc.get("version"),
        }
        if rule:
            for k, v in fields.items():
                setattr(rule, k, v)
        else:
            rule = DetectionRule(**fields)
            db.add(rule)
        created_or_updated.append(rule)
    if created_or_updated:
        db.commit()
        for r in created_or_updated:
            db.refresh(r)
    return created_or_updated
