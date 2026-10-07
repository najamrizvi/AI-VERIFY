import sys

sys.path.insert(0, "g02_repository")

from domain.models import Order
from domain.repository import OrderRepository
from services.order_service import OrderService


class FailingPaymentService:
    def process_payment(self, payment):
        return False


def test_failed_payment_does_not_mark_order_as_paid():
    order_repository = OrderRepository()
    payment_service = FailingPaymentService()

    service = OrderService(
        order_repository,
        payment_service,
    )

    order = Order(
        order_id="O5001",
        user_id="U001",
        amount=150.0,
    )

    service.create_order(order)

    result = service.pay_order("O5001")

    assert result is False
    assert service.get_order("O5001").status == "pending"
