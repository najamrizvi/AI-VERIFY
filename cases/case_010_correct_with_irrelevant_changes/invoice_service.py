from dataclasses import dataclass


@dataclass
class InvoiceRequest:
    user_id: str
    invoice_id: str
    amount: float


class InvoiceService:
    def create_invoice(self, request: InvoiceRequest):
        if request.amount < 0:
            return None

        return request

    def format_invoice_id(self, request: InvoiceRequest):
        return f"INV-{request.invoice_id}"

    def get_service_name(self):
        return "InvoiceService"
