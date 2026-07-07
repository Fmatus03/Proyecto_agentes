from app.domain.rules import available_stock, ensure_non_negative, ensure_positive, line_profit, suggested_unit_price


def confirm_sale(current_stock: float, active_reservations: float, quantity: float, unit_price: float, unit_cost: float) -> dict[str, float | str]:
    ensure_positive(quantity, "quantity")
    if quantity > available_stock(current_stock, active_reservations):
        raise ValueError("stock_unavailable")
    return {"movement": "VENTA", "remaining_stock": current_stock - quantity, "profit": line_profit(unit_price, unit_cost, quantity)}


def price_for_customer_type(base_price: float, discount_pct: float, quantity: float, dozen_price: float = 0) -> dict[str, float | str]:
    price = suggested_unit_price(base_price, discount_pct, quantity, dozen_price)
    warning = "price_zero" if price == 0 else ""
    return {"precio_unitario": price, "warning": warning}


def release_reservation(quantity: float) -> dict[str, float | str]:
    return {"released": ensure_positive(quantity, "quantity"), "status": "liberada"}


def consume_reservation(quantity: float, unit_price: float, unit_cost: float) -> dict[str, float | str]:
    qty = ensure_positive(quantity, "quantity")
    price = ensure_non_negative(unit_price, "unit_price")
    cost = ensure_non_negative(unit_cost, "unit_cost")
    return {"consumed": qty, "status": "consumida", "profit": line_profit(price, cost, qty)}
