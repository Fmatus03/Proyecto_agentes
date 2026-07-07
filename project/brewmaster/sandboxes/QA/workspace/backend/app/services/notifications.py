from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app.domain.rules import email_status_after_attempt, normalize_email_list, should_send_stock_alert


@dataclass
class MockEmailSender:
    failures_before_success: int = 0
    attempts: int = 0

    def send(self, recipients: list[str], subject: str, body_html: str) -> bool:
        if not recipients:
            raise ValueError("recipients_required")
        self.attempts += 1
        return self.attempts > self.failures_before_success


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_stock_alert(supply: dict[str, Any], hours_since_last_alert: float | None) -> dict[str, Any] | None:
    if not supply.get("enable_email_alerts"):
        return None
    recipients = normalize_email_list(supply.get("alert_emails", []))
    if not recipients:
        raise ValueError("alert_recipients_required")
    if not should_send_stock_alert(float(supply.get("stock_actual", 0)), float(supply.get("stock_minimo", 0)), hours_since_last_alert):
        return None
    return {
        "supply_id": supply["id"],
        "recipients": recipients,
        "subject": f"Stock bajo: {supply['nombre']}",
        "body_html": f"<p>{supply['nombre']} bajo minimo configurado.</p>",
        "status": "queued",
        "attempts": 0,
        "sent_at": None,
        "error_message": "",
        "final_error": False,
    }


def process_notification(notification: dict[str, Any], sender: MockEmailSender, max_attempts: int = 5) -> dict[str, Any]:
    if notification.get("status") == "sent" or notification.get("final_error"):
        return notification
    try:
        success = sender.send(
            list(notification.get("recipients", [])),
            str(notification.get("subject", "")),
            str(notification.get("body_html", "")),
        )
        status = email_status_after_attempt(int(notification.get("attempts", 0)), success, max_attempts)
        notification.update(status)
        notification["error_message"] = "" if success else "mock_smtp_error"
        notification["sent_at"] = now_iso() if success else None
        notification["updated_at"] = now_iso()
        return notification
    except Exception as exc:
        status = email_status_after_attempt(int(notification.get("attempts", 0)), False, max_attempts)
        notification.update(status)
        notification["error_message"] = str(exc)
        notification["updated_at"] = now_iso()
        return notification
