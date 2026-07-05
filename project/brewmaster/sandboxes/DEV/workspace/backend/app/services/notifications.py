from app.domain.rules import should_send_stock_alert


def enqueue_stock_alert(current_stock: float, minimum_stock: float, hours_since_last_alert: float | None) -> dict[str, object]:
    if not should_send_stock_alert(current_stock, minimum_stock, hours_since_last_alert):
        return {"queued": False, "reason": "interval_or_threshold_not_met"}
    return {"queued": True, "status": "pendiente", "max_attempts": 5}
