from datetime import datetime, timezone
from typing import Any


def ok(data: Any, request_id: str = "REQ-LOCAL") -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id, "timestamp": datetime.now(timezone.utc).isoformat()}}


def error(code: str, message: str, details: list[dict[str, str]] | None = None, request_id: str = "REQ-LOCAL") -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": details or []}, "meta": {"request_id": request_id}}
