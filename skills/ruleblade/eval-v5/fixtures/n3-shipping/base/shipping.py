import math


def shipping_fee(weight_kg: float) -> int:
    """运费规则：首重 1kg 收 10 元，续重每 1kg 加 5 元，不足 1kg 按 1kg 计。"""
    if weight_kg <= 0:
        raise ValueError("weight must be positive")
    extra = max(0, math.ceil(weight_kg) - 1)
    return 10 + extra * 5
