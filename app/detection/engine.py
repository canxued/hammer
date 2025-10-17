from __future__ import annotations
from typing import Any, Dict, List
import re
from sqlalchemy.orm import Session

from ..models import DetectionRule, Alert, Event
from ..alerting.notifier import send_alert
from ..utils import deep_get, ip_in_cidr

SUPPORTED_OPS = {"equals", "contains", "regex", "in", "in_cidr", "gt", "lt"}


def _evaluate_predicate(event_obj: Dict[str, Any], pred: Dict[str, Any]) -> bool:
    if "all" in pred:
        return all(_evaluate_predicate(event_obj, p) for p in pred["all"])
    if "any" in pred:
        return any(_evaluate_predicate(event_obj, p) for p in pred["any"])

    field = pred.get("field")
    op = pred.get("op", "equals")
    value = pred.get("value")
    if field is None:
        return False
    actual = deep_get(event_obj, field)

    if op == "equals":
        return actual == value
    if op == "contains":
        if actual is None or value is None:
            return False
        return str(value).lower() in str(actual).lower()
    if op == "regex":
        if actual is None or value is None:
            return False
        return re.search(str(value), str(actual)) is not None
    if op == "in":
        try:
            return actual in value
        except Exception:
            return False
    if op == "in_cidr":
        if not isinstance(value, str) or not isinstance(actual, str):
            return False
        return ip_in_cidr(actual, value)
    if op == "gt":
        try:
            return float(actual) > float(value)
        except Exception:
            return False
    if op == "lt":
        try:
            return float(actual) < float(value)
        except Exception:
            return False

    return False


def evaluate_rule(conditions: Dict[str, Any], event_obj: Dict[str, Any]) -> bool:
    if not conditions:
        return False
    return _evaluate_predicate(event_obj, conditions)


def event_to_match_object(event: Event) -> Dict[str, Any]:
    base = {
        "source": event.source,
        "event_time": event.event_time.isoformat() if event.event_time else None,
        "src_ip": event.src_ip,
        "dst_ip": event.dst_ip,
        "hostname": event.hostname,
        "username": event.username,
        "process_name": event.process_name,
        "event_type": event.event_type,
        "raw": event.raw or {},
    }
    return base


def process_event_rules(db: Session, event: Event) -> List[Alert]:
    created: List[Alert] = []
    rules: List[DetectionRule] = db.query(DetectionRule).filter(DetectionRule.enabled == 1).all()
    event_obj = event_to_match_object(event)
    for rule in rules:
        try:
            if evaluate_rule(rule.conditions, event_obj):
                alert = Alert(
                    severity=rule.severity or "medium",
                    title=rule.name,
                    rule_name=rule.name,
                    event_id=event.id,
                    details={"rule_id": rule.id, "description": rule.description},
                )
                db.add(alert)
                created.append(alert)
        except Exception:
            # Skip invalid rule
            continue
    if created:
        db.commit()
        for a in created:
            db.refresh(a)
            send_alert({
                "id": a.id,
                "severity": a.severity,
                "title": a.title,
                "rule_name": a.rule_name,
                "event_id": a.event_id,
            })
    return created
