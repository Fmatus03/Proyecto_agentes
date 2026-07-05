from app.domain.rules import CostInput, batch_cost, ensure_positive


def complete_batch(cost_input: CostInput, stock_ok: bool) -> dict[str, object]:
    if not stock_ok:
        raise ValueError("stock_unavailable")
    ensure_positive(cost_input.produced_liters, "produced_liters")
    return {"state": "completado", "cost": batch_cost(cost_input), "kardex": "SALIDA_PRODUCCION"}
