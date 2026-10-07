from invoice_service import InvoiceRequest, InvoiceService


def test_positive_amount_is_accepted():
    service = InvoiceService()
    request = InvoiceRequest("U1", "I601", 100)

    result = service.create_invoice(request)

    assert result == request


def test_zero_amount_is_accepted():
    service = InvoiceService()
    request = InvoiceRequest("U1", "I602", 0)

    result = service.create_invoice(request)

    assert result == request


def test_negative_amount_is_rejected():
    service = InvoiceService()
    request = InvoiceRequest("U1", "I603", -1)

    result = service.create_invoice(request)

    assert result is None


def test_large_negative_amount_is_rejected():
    service = InvoiceService()
    request = InvoiceRequest("U1", "I604", -100)

    result = service.create_invoice(request)

    assert result is None


def test_unrelated_invoice_id_formatting():
    service = InvoiceService()
    request = InvoiceRequest("U1", "I605", 100)

    assert service.format_invoice_id(request) == "INV-I605"


def test_service_name():
    service = InvoiceService()

    assert service.get_service_name() == "InvoiceService"
