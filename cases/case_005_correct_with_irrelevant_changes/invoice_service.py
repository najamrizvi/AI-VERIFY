from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: str
    name: str


@dataclass(frozen=True)
class Invoice:
    id: str
    user_id: str
    amount: float


class InvoiceService:
    def __init__(self, invoices: list[Invoice]):
        self.invoices = {invoice.id: invoice for invoice in invoices}

    def get_invoice(self, invoice_id: str, authenticated_user: User) -> Invoice | None:
        invoice = self.invoices.get(invoice_id)

        if invoice is None:
            return None

        # Requirement-relevant authorization.
        if invoice.user_id != authenticated_user.id:
            return None

        return invoice

    def invoice_count(self) -> int:
        # Irrelevant change: informational helper.
        return len(self.invoices)

    def service_name(self) -> str:
        # Irrelevant change: metadata.
        return "Invoice Service"
