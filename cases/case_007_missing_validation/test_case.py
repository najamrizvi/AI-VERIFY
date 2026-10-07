from invoice_service import InvoiceRequest, InvoiceService


def test_positive_amount_is_accepted():
    service = InvoiceService()
    request = InvoiceRequest("U1", "I301", 100)

    result = service.create_invoice(request)

    assert result == request


def test_zero_amount_is_accepted():
    service = InvoiceService()
    request = InvoiceRequest("U1", "I302", 0)

    result = service.create_invoice(request)

    assert result == request


def test_negative_amount_is_rejected():
    service = InvoiceService()
    request = InvoiceRequest("U1", "I303", -1)

    result = service.create_invoice(request)

    assert result is None


def test_large_negative_amount_is_rejected():
    service = InvoiceService()
    request = InvoiceRequest("U1", "I304", -100)

    result = service.create_invoice(request)

    assert result is None
