from app.domain.rules import available_stock, ensure_positive, line_profit


def confirm_sale(current_stock: float, active_reservations: float, quantity: float, unit_price: float, unit_cost: float) -> dict[str, float | str]:
    ensure_positive(quantity, "quantity")
    if quantity > available_stock(current_stock, active_reservations):
        raise ValueError("stock_unavailable")
    return {"movement": "VENTA", "remaining_stock": current_stock - quantity, "profit": line_profit(unit_price, unit_cost, quantity)}
