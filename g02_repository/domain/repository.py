from domain.models import Order, Payment


class OrderRepository:
    def __init__(self):
        self._orders = {}

    def save(self, order: Order):
        self._orders[order.order_id] = order

    def get(self, order_id: str):
        return self._orders.get(order_id)


class PaymentRepository:
    def __init__(self):
        self._payments = {}

    def save(self, payment: Payment):
        self._payments[payment.payment_id] = payment

    def get_by_order_id(self, order_id: str):
        for payment in self._payments.values():
            if payment.order_id == order_id:
                return payment
        return None
