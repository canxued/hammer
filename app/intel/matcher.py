from __future__ import annotations
from typing import List
from sqlalchemy.orm import Session

from ..models import ThreatIntelIndicator, Alert, Event
from ..alerting.notifier import send_alert


INDICATOR_TO_FIELDS = {
    "ip": ["src_ip", "dst_ip", "raw.destination.ip", "raw.source.ip"],
    "domain": ["hostname", "raw.domain", "raw.dns.rrname"],
    "url": ["raw.url", "raw.http.url"],
    "hash": ["raw.hash", "raw.sha256", "raw.md5"],
}

from ..utils import deep_get


def match_event_intel(db: Session, event: Event) -> List[Alert]:
    created: List[Alert] = []
    indicators = db.query(ThreatIntelIndicator).all()
    if not indicators:
        return created
    for ind in indicators:
        fields = INDICATOR_TO_FIELDS.get(ind.type, [])
        for f in fields:
            val = deep_get({
                "src_ip": event.src_ip,
                "dst_ip": event.dst_ip,
                "hostname": event.hostname,
                "raw": event.raw or {},
            }, f)
            if val and str(val).lower() == ind.value.lower():
                alert = Alert(
                    severity=ind.severity or "medium",
                    title=f"Threat intel match: {ind.value}",
                    indicator_value=ind.value,
                    event_id=event.id,
                    details={"indicator_type": ind.type, "source": ind.source},
                )
                db.add(alert)
                created.append(alert)
                break
    if created:
        db.commit()
        for a in created:
            db.refresh(a)
            send_alert({
                "id": a.id,
                "severity": a.severity,
                "title": a.title,
                "indicator_value": a.indicator_value,
                "event_id": a.event_id,
            })
    return created
