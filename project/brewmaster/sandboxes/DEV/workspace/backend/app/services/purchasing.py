from app.domain.rules import ensure_non_negative, ensure_positive, purchase_order_state_after_receipt


def receive_order(requested: float, already_received: float, incoming: float, allow_over_receive: bool = False) -> dict[str, float | str]:
    ensure_positive(incoming, "incoming")
    pending = requested - already_received
    if incoming > pending and not allow_over_receive:
        raise ValueError("state_conflict")
    new_received = already_received + incoming
    status = "recibida" if new_received >= requested else "parcialmente_recibida"
    return {"cantidad_recibida": new_received, "estado": status, "movement": "ENTRADA"}


def order_line_total(quantity: float, unit_price: float) -> float:
    return round(ensure_positive(quantity, "quantity") * ensure_non_negative(unit_price, "unit_price"), 4)


def editable_order_state(state: str) -> bool:
    return state == "borrador"


def receipt_state(requested: float, received: float) -> str:
    return purchase_order_state_after_receipt(requested, received)
