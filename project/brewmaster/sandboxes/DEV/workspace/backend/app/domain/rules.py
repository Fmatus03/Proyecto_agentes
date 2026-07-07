from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_ALERT_INTERVAL_HOURS = 24
MAX_EMAIL_ATTEMPTS = 5
QUALITY_RESULTS = {"aprobado", "rechazado"}


@dataclass(frozen=True)
class CostInput:
    supplies: float
    labor_hours: float
    labor_rate: float
    energy_kwh: float
    energy_rate: float
    water_liters: float
    water_rate: float
    waste_cost: float
    indirect_cost: float
    presentation_cost: float
    produced_liters: float
    produced_units: int


def ensure_positive(value: float, field: str) -> float:
    number = float(value)
    if number <= 0:
        raise ValueError(f"{field}_must_be_greater_than_zero")
    return number


def ensure_non_negative(value: float, field: str) -> float:
    number = float(value)
    if number < 0:
        raise ValueError(f"{field}_must_be_greater_or_equal_zero")
    return number


def available_stock(current_stock: float, active_reservations: float = 0) -> float:
    value = float(current_stock) - float(active_reservations)
    return value if value > 0 else 0


def normalize_email_list(values: list[str] | str) -> list[str]:
    raw_values = values
    if isinstance(raw_values, str):
        raw_values = [item.strip() for item in raw_values.split(",")]
    if not isinstance(raw_values, list):
        raise ValueError("email_list_invalid")
    normalized: list[str] = []
    for value in raw_values:
        email = str(value or "").strip().lower()
        if not email:
            continue
        if not EMAIL_RE.match(email):
            raise ValueError("email_invalid")
        if email not in normalized:
            normalized.append(email)
    return normalized


def should_send_stock_alert(current_stock: float, minimum_stock: float, hours_since_last_alert: float | None) -> bool:
    current = float(current_stock)
    minimum = float(minimum_stock)
    if current <= 0:
        return True
    if current >= minimum:
        return False
    return hours_since_last_alert is None or hours_since_last_alert >= MIN_ALERT_INTERVAL_HOURS


def validate_alert_configuration(enabled: bool, recipients: list[str] | str) -> list[str]:
    normalized = normalize_email_list(recipients)
    if enabled and not normalized:
        raise ValueError("alert_recipients_required")
    return normalized


def email_status_after_attempt(current_attempts: int, success: bool, max_attempts: int = MAX_EMAIL_ATTEMPTS) -> dict[str, object]:
    attempts = int(current_attempts) + 1
    if success:
        return {"status": "sent", "attempts": attempts, "final_error": False}
    if attempts >= max_attempts:
        return {"status": "failed", "attempts": attempts, "final_error": True}
    return {"status": "queued", "attempts": attempts, "final_error": False}


def local_secret_marker(raw_secret: str, username: str) -> str:
    if not raw_secret:
        raise ValueError("smtp_secret_required")
    digest = hashlib.sha256(f"{username}:{raw_secret}".encode("utf-8")).hexdigest()
    return f"local-encrypted:{digest}"


def batch_cost(data: CostInput) -> dict[str, float]:
    for field, value in data.__dict__.items():
        if field != "produced_units":
            ensure_non_negative(float(value), field)
    ensure_positive(data.produced_liters, "produced_liters")
    ensure_positive(float(data.produced_units), "produced_units")
    total = (
        data.supplies
        + data.labor_hours * data.labor_rate
        + data.energy_kwh * data.energy_rate
        + data.water_liters * data.water_rate
        + data.waste_cost
        + data.indirect_cost
        + data.presentation_cost * data.produced_units
    )
    return {
        "total": round(total, 4),
        "cost_per_liter": round(total / data.produced_liters, 4),
        "cost_per_unit": round(total / data.produced_units, 4),
    }


def batch_supply_consumption(recipe_quantity: float, recipe_volume: float, produced_liters: float) -> float:
    ensure_positive(recipe_quantity, "recipe_quantity")
    ensure_positive(recipe_volume, "recipe_volume")
    ensure_positive(produced_liters, "produced_liters")
    return round(float(recipe_quantity) * float(produced_liters) / float(recipe_volume), 4)


def validate_quality_result(result: str, rejection_reason: str = "") -> str:
    normalized = str(result or "").strip()
    if normalized not in QUALITY_RESULTS:
        raise ValueError("quality_result_invalid")
    if normalized == "rechazado" and not str(rejection_reason or "").strip():
        raise ValueError("quality_rejection_reason_required")
    return normalized


def waste_total(quantity: float, unit_cost: float) -> float:
    return round(ensure_positive(quantity, "waste_quantity") * ensure_non_negative(unit_cost, "waste_unit_cost"), 4)

def line_profit(unit_price: float, unit_cost: float, quantity: float) -> float:
    ensure_positive(quantity, "quantity")
    ensure_non_negative(unit_price, "unit_price")
    ensure_non_negative(unit_cost, "unit_cost")
    return round((float(unit_price) - float(unit_cost)) * float(quantity), 4)


def suggested_unit_price(base_price: float, discount_pct: float, quantity: float, dozen_price: float = 0) -> float:
    ensure_positive(quantity, "quantity")
    base = ensure_non_negative(base_price, "base_price")
    discount = ensure_non_negative(discount_pct, "discount_pct")
    if discount > 100:
        raise ValueError("discount_pct_invalid")
    if quantity >= 12 and float(dozen_price or 0) > 0:
        return round(ensure_non_negative(dozen_price, "dozen_price") / 12, 4)
    return round(base * (1 - discount / 100), 4)


def purchase_order_state_after_receipt(requested: float, received: float) -> str:
    ensure_positive(requested, "requested")
    ensure_non_negative(received, "received")
    if received > requested:
        raise ValueError("receipt_exceeds_pending")
    return "recibida" if received == requested else "parcialmente_recibida"
