from dataclasses import dataclass


@dataclass
class InvoiceRequest:
    user_id: str
    invoice_id: str
    amount: object


class InvoiceService:
    def create_invoice(self, request: InvoiceRequest):
        if isinstance(request.amount, (int, float)):
            if request.amount < 0:
                return None

        return request
