from invoice_service import InvoiceRequest, InvoiceService


def test_standard_creation_rejects_negative_amount():
    service = InvoiceService()
    request = InvoiceRequest("U1", "I401", -100)

    result = service.create_invoice(request)

    assert result is None


def test_standard_creation_accepts_positive_amount():
    service = InvoiceService()
    request = InvoiceRequest("U1", "I402", 100)

    result = service.create_invoice(request)

    assert result == request


def test_bulk_creation_accepts_valid_amounts():
    service = InvoiceService()
    requests = [
        InvoiceRequest("U1", "I403", 100),
        InvoiceRequest("U1", "I404", 250),
    ]

    result = service.bulk_create_invoices(requests)

    assert result == requests


def test_bulk_creation_rejects_negative_amount():
    service = InvoiceService()
    requests = [
        InvoiceRequest("U1", "I405", -50),
    ]

    result = service.bulk_create_invoices(requests)

    assert result == []
