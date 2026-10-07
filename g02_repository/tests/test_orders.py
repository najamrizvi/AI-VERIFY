import sys

sys.path.insert(0, "g02_repository")

from domain.models import Order
from domain.repository import OrderRepository, PaymentRepository
from services.payment_service import PaymentService
from services.order_service import OrderService


def build_order_service():
    order_repository = OrderRepository()
    payment_repository = PaymentRepository()
    payment_service = PaymentService(payment_repository)

    return OrderService(
        order_repository,
        payment_service,
    )


def test_order_can_be_created():
    service = build_order_service()

    order = Order("O3001", "U001", 100.0)

    created = service.create_order(order)

    assert created.order_id == "O3001"
    assert created.status == "pending"


def test_successful_payment_marks_order_as_paid():
    service = build_order_service()

    order = Order("O3002", "U001", 200.0)
    service.create_order(order)

    result = service.pay_order("O3002")

    assert result is True
    assert service.get_order("O3002").status == "paid"
