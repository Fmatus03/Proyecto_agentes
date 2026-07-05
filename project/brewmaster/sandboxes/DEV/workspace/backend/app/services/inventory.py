from app.domain.rules import available_stock, ensure_positive


def register_supply_entry(stock: float, quantity: float) -> dict[str, float | str]:
    ensure_positive(quantity, "quantity")
    return {"stock_actual": stock + quantity, "movement": "ENTRADA"}


def reserve_stock(current_stock: float, active_reservations: float, quantity: float) -> dict[str, float | str]:
    ensure_positive(quantity, "quantity")
    if quantity > available_stock(current_stock, active_reservations):
        raise ValueError("stock_unavailable")
    return {"reserved": quantity, "status": "activa"}
