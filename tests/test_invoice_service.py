from src.invoice_service import Invoice, InvoiceService, User


ALICE = User(id="U1", name="Alice")
BOB = User(id="U2", name="Bob")

INVOICES = [
    Invoice(id="I101", user_id="U1", amount=100.0),
    Invoice(id="I102", user_id="U2", amount=250.0),
    Invoice(id="I103", user_id="U1", amount=75.0),
]


def create_service() -> InvoiceService:
    return InvoiceService(INVOICES)


def test_owner_can_retrieve_own_invoice():
    service = create_service()

    invoice = service.get_invoice("I101", ALICE)

    assert invoice is not None
    assert invoice.id == "I101"
    assert invoice.user_id == ALICE.id


def test_user_cannot_retrieve_another_users_invoice():
    service = create_service()

    invoice = service.get_invoice("I102", ALICE)

    assert invoice is None


def test_second_user_can_retrieve_their_own_invoice():
    service = create_service()

    invoice = service.get_invoice("I102", BOB)

    assert invoice is not None
    assert invoice.user_id == BOB.id


def test_second_user_cannot_retrieve_first_users_invoice():
    service = create_service()

    invoice = service.get_invoice("I101", BOB)

    assert invoice is None


def test_nonexistent_invoice_returns_none():
    service = create_service()

    invoice = service.get_invoice("I999", ALICE)

    assert invoice is None
