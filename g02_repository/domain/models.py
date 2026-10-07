from dataclasses import dataclass


@dataclass
class Order:
    order_id: str
    user_id: str
    amount: float
    status: str = "pending"


@dataclass
class Payment:
    payment_id: str
    order_id: str
    amount: float
    status: str = "pending"
