from app.domain.rules import ensure_positive


def receive_order(requested: float, already_received: float, incoming: float, allow_over_receive: bool = False) -> dict[str, float | str]:
    ensure_positive(incoming, "incoming")
    pending = requested - already_received
    if incoming > pending and not allow_over_receive:
        raise ValueError("state_conflict")
    new_received = already_received + incoming
    status = "recibida" if new_received >= requested else "parcialmente_recibida"
    return {"cantidad_recibida": new_received, "estado": status, "movement": "ENTRADA"}
