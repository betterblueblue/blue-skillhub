from .models import Order


def can_ship(order: Order) -> bool:
    return order.status == "paid"


def refund(order: Order) -> None:
    if order.status != "paid":
        raise ValueError("only paid orders can be refunded")
    order.status = "refunded"
