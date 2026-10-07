from domain.models import Order
from domain.repository import OrderRepository, PaymentRepository
from services.payment_service import PaymentService
from services.order_service import OrderService


class OrderAPI:
    def __init__(self):
        order_repository = OrderRepository()
        payment_repository = PaymentRepository()

        payment_service = PaymentService(payment_repository)

        self.order_service = OrderService(
            order_repository,
            payment_service,
        )

    def create_order(self, order_id: str, user_id: str, amount: float):
        order = Order(
            order_id=order_id,
            user_id=user_id,
            amount=amount,
        )

        created_order = self.order_service.create_order(order)

        return {
            "order_id": created_order.order_id,
            "status": created_order.status,
        }

    def pay_order(self, order_id: str):
        success = self.order_service.pay_order(order_id)

        return {
            "order_id": order_id,
            "success": success,
        }

    def get_order(self, order_id: str):
        order = self.order_service.get_order(order_id)

        if order is None:
            return None

        return {
            "order_id": order.order_id,
            "user_id": order.user_id,
            "amount": order.amount,
            "status": order.status,
        }
