from domain.models import Order, Payment
from domain.repository import OrderRepository
from services.payment_service import PaymentService


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        payment_service: PaymentService,
    ):
        self.order_repository = order_repository
        self.payment_service = payment_service

    def create_order(self, order: Order):
        self.order_repository.save(order)
        return order

    def pay_order(self, order_id: str) -> bool:
        order = self.order_repository.get(order_id)

        if order is None:
            return False

        payment = Payment(
            payment_id=f"P-{order.order_id}",
            order_id=order.order_id,
            amount=order.amount,
        )

        payment_successful = self.payment_service.process_payment(payment)

        if not payment_successful:
            return False

        order.status = "paid"
        self.order_repository.save(order)
        return True

    def get_order(self, order_id: str):
        return self.order_repository.get(order_id)
