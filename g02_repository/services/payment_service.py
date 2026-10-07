from domain.models import Payment
from domain.repository import PaymentRepository


class PaymentService:
    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository = payment_repository

    def process_payment(self, payment: Payment) -> bool:
        payment.status = "completed"
        self.payment_repository.save(payment)
        return True

    def get_payment_for_order(self, order_id: str):
        return self.payment_repository.get_by_order_id(order_id)
