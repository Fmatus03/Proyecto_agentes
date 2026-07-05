from __future__ import annotations

from dataclasses import dataclass


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


def available_stock(current_stock: float, active_reservations: float) -> float:
    value = current_stock - active_reservations
    return value if value > 0 else 0


def ensure_positive(value: float, field: str) -> None:
    if value <= 0:
        raise ValueError(f"{field}_must_be_greater_than_zero")


def ensure_non_negative(value: float, field: str) -> None:
    if value < 0:
        raise ValueError(f"{field}_must_be_greater_or_equal_zero")


def line_profit(unit_price: float, unit_cost: float, quantity: float) -> float:
    ensure_positive(quantity, "quantity")
    return (unit_price - unit_cost) * quantity


def should_send_stock_alert(current_stock: float, minimum_stock: float, hours_since_last_alert: float | None) -> bool:
    if current_stock <= 0:
        return True
    if current_stock >= minimum_stock:
        return False
    return hours_since_last_alert is None or hours_since_last_alert >= 24


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
