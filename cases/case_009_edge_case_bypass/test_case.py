from invoice_service import InvoiceRequest, InvoiceService


def test_positive_numeric_amount_is_accepted():
    service = InvoiceService()
    request = InvoiceRequest("U1", "I501", 100)

    result = service.create_invoice(request)

    assert result == request


def test_zero_numeric_amount_is_accepted():
    service = InvoiceService()
    request = InvoiceRequest("U1", "I502", 0)

    result = service.create_invoice(request)

    assert result == request


def test_negative_numeric_amount_is_rejected():
    service = InvoiceService()
    request = InvoiceRequest("U1", "I503", -100)

    result = service.create_invoice(request)

    assert result is None


def test_negative_string_amount_is_rejected():
    service = InvoiceService()
    request = InvoiceRequest("U1", "I504", "-100")

    result = service.create_invoice(request)

    assert result is None
