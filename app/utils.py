from __future__ import annotations
from typing import Any, Optional
import ipaddress

SENTINEL = object()

def deep_get(obj: Any, path: str, default: Any = None) -> Any:
    if not path:
        return obj
    parts = path.split('.')
    cur: Any = obj
    for part in parts:
        if cur is None:
            return default
        if isinstance(cur, dict):
            cur = cur.get(part, default)
        else:
            cur = getattr(cur, part, default)
    return cur

def ip_in_cidr(ip_value: str, cidr: str) -> bool:
    try:
        ip_obj = ipaddress.ip_address(ip_value)
        network = ipaddress.ip_network(cidr, strict=False)
        return ip_obj in network
    except Exception:
        return False
