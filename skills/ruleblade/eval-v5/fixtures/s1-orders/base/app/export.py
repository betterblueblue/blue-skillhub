from .models import Order


def to_row(order: Order) -> dict:
    return {"id": order.id, "amount": order.amount, "state": order.state}
