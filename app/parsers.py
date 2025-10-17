from __future__ import annotations
from typing import Dict, Any

# Simple normalizers to extract common fields from different sources

def normalize_event_fields(source: str, raw: Dict[str, Any]) -> Dict[str, Any]:
    raw = raw or {}
    src_ip = None
    dst_ip = None
    hostname = None
    username = None
    process_name = None
    event_type = None

    if source == "suricata":
        event_type = raw.get("event_type") or raw.get("type")
        # DNS
        if "dns" in raw:
            src_ip = raw.get("src_ip")
            dst_ip = raw.get("dest_ip") or raw.get("dst_ip")
            hostname = (raw.get("dns") or {}).get("rrname")
        # HTTP
        if "http" in raw:
            src_ip = raw.get("src_ip")
            dst_ip = raw.get("dest_ip") or raw.get("dst_ip")
        # Flow/alert
        if raw.get("alert"):
            event_type = event_type or "alert"
    elif source == "sysmon":
        event_type = raw.get("EventIDName") or raw.get("event_type")
        if event_type is None and raw.get("EventID") == 1:
            event_type = "ProcessCreate"
        hostname = raw.get("Computer") or raw.get("host")
        username = raw.get("User") or raw.get("user")
        process_name = raw.get("Image") or raw.get("process")
        src_ip = raw.get("SourceIp") or raw.get("src_ip")
        dst_ip = raw.get("DestinationIp") or raw.get("dst_ip")
    else:
        # generic common fields
        src_ip = raw.get("src_ip") or raw.get("source.ip")
        dst_ip = raw.get("dst_ip") or raw.get("destination.ip")
        hostname = raw.get("host") or raw.get("hostname")
        username = raw.get("user") or raw.get("username")
        process_name = raw.get("process") or raw.get("image")
        event_type = raw.get("event_type") or raw.get("type")

    return {
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "hostname": hostname,
        "username": username,
        "process_name": process_name,
        "event_type": event_type,
    }
