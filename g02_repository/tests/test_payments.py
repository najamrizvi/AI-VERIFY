import sys

sys.path.insert(0, "g02_repository")

from domain.models import Payment
from domain.repository import PaymentRepository
from services.payment_service import PaymentService


def build_payment_service():
    repository = PaymentRepository()
    return PaymentService(repository)


def test_payment_can_be_processed():
    service = build_payment_service()

    payment = Payment(
        payment_id="P3001",
        order_id="O3001",
        amount=100.0,
    )

    result = service.process_payment(payment)

    assert result is True
    assert payment.status == "completed"


def test_completed_payment_is_persisted():
    service = build_payment_service()

    payment = Payment(
        payment_id="P3002",
        order_id="O3002",
        amount=200.0,
    )

    service.process_payment(payment)

    stored = service.get_payment_for_order("O3002")

    assert stored is not None
    assert stored.payment_id == "P3002"
    assert stored.status == "completed"
