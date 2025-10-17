from __future__ import annotations
from typing import Optional
import json

# Simple console notifier; can be extended to email/webhook

def send_alert(alert_dict: dict, sink: Optional[str] = None) -> None:
    line = json.dumps(alert_dict, ensure_ascii=False)
    print(f"[ALERT] {line}")
