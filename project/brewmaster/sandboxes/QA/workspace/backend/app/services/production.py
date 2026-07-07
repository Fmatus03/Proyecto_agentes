from __future__ import annotations

from typing import Any

from app.domain.rules import (
    CostInput,
    batch_cost,
    batch_supply_consumption,
    ensure_non_negative,
    ensure_positive,
    validate_quality_result,
    waste_total,
)


def planned_consumption(recipe: dict[str, Any], produced_liters: float) -> list[dict[str, float | int | str]]:
    recipe_volume = ensure_positive(recipe["volumen_por_lote"], "recipe_volume")
    items: list[dict[str, float | int | str]] = []
    for ingredient in recipe.get("ingredientes", []):
        quantity = batch_supply_consumption(float(ingredient["cantidad"]), recipe_volume, produced_liters)
        items.append(
            {
                "supply_id": int(ingredient["supply_id"]),
                "nombre_insumo": str(ingredient.get("nombre_insumo", "")),
                "cantidad_usada": quantity,
                "costo_unitario": ensure_non_negative(float(ingredient.get("costo_unitario", 0)), "costo_unitario"),
            }
        )
    return items


def stock_failures(requirements: list[dict[str, Any]], current_stock: dict[int, float]) -> list[dict[str, float | int]]:
    failures: list[dict[str, float | int]] = []
    for item in requirements:
        supply_id = int(item["supply_id"])
        required = float(item["cantidad_usada"])
        available = float(current_stock.get(supply_id, 0))
        if required > available:
            failures.append({"supply_id": supply_id, "required": required, "available": available})
    return failures


def complete_batch(cost_input: CostInput, stock_ok: bool) -> dict[str, object]:
    if not stock_ok:
        raise ValueError("stock_unavailable")
    ensure_positive(cost_input.produced_liters, "produced_liters")
    return {"state": "completado", "cost": batch_cost(cost_input), "kardex": "SALIDA_PRODUCCION"}


def quality_payload(result: str, rejection_reason: str = "") -> dict[str, str]:
    return {"resultado": validate_quality_result(result, rejection_reason), "motivo_rechazo": rejection_reason}


def waste_payload(entity_type: str, quantity: float, unit_cost: float, reason: str) -> dict[str, object]:
    if entity_type not in {"insumo", "producto"}:
        raise ValueError("waste_entity_invalid")
    if not reason.strip():
        raise ValueError("waste_reason_required")
    return {
        "tipo_entidad": entity_type,
        "cantidad_perdida": ensure_positive(quantity, "waste_quantity"),
        "costo_total": waste_total(quantity, unit_cost),
        "motivo_detallado": reason.strip(),
        "movement": "MERMA",
    }
