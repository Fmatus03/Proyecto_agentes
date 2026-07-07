from __future__ import annotations

from typing import Any

from app.domain.rules import ensure_non_negative, ensure_positive, should_send_stock_alert


ACTIVE_STATES = {"activo", "en_prueba"}


def ensure_active(record: dict[str, Any], label: str) -> dict[str, Any]:
    if record.get("estado") not in ACTIVE_STATES:
        raise ValueError(f"{label}_inactive")
    return record


def recipe_estimated_cost(ingredients: list[dict[str, float]]) -> float:
    if not ingredients:
        raise ValueError("recipe_ingredients_required")
    total = 0.0
    for ingredient in ingredients:
        quantity = ensure_positive(float(ingredient["cantidad"]), "ingredient_quantity")
        unit_cost = ensure_non_negative(float(ingredient["costo_unitario"]), "ingredient_unit_cost")
        total += quantity * unit_cost
    return round(total, 4)


def can_inactivate_supply(supply_id: int, recipes: list[dict[str, Any]]) -> bool:
    for recipe in recipes:
        if recipe.get("estado") not in ACTIVE_STATES:
            continue
        if any(int(item.get("supply_id", 0)) == supply_id for item in recipe.get("ingredientes", [])):
            return False
    return True


def register_supply_entry(stock: float, quantity: float, unit_cost: float, minimum_stock: float, hours_since_last_alert: float | None) -> dict[str, object]:
    current_stock = ensure_non_negative(stock, "stock")
    entry_quantity = ensure_positive(quantity, "quantity")
    cost = ensure_non_negative(unit_cost, "unit_cost")
    resulting_stock = round(current_stock + entry_quantity, 4)
    alert_needed = should_send_stock_alert(resulting_stock, minimum_stock, hours_since_last_alert)
    recovered = resulting_stock >= float(minimum_stock)
    return {
        "stock_actual": resulting_stock,
        "movement": "ENTRADA",
        "cantidad": entry_quantity,
        "costo_unitario": cost,
        "saldo_resultante": resulting_stock,
        "alert_needed": alert_needed,
        "reset_last_alert": recovered,
    }


def low_stock_items(supplies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        supply
        for supply in supplies
        if supply.get("estado") == "activo"
        and float(supply.get("stock_actual", 0)) < float(supply.get("stock_minimo", 0))
    ]

def reserve_stock(current_stock: float, active_reservations: float, quantity: float) -> dict[str, float | str]:
    requested = ensure_positive(quantity, "quantity")
    free_stock = max(float(current_stock) - float(active_reservations), 0)
    if requested > free_stock:
        raise ValueError("stock_unavailable")
    return {"reserved": requested, "available_after": round(free_stock - requested, 4), "status": "activa"}
