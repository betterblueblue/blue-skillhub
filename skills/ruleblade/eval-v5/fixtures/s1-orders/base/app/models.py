from dataclasses import dataclass


@dataclass
class Order:
    id: int
    amount: int
    status: str = "unpaid"  # 支付状态：unpaid / paid / refunded
    state: str = "draft"  # 展示状态：draft / published
