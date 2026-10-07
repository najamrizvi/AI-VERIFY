import sys
from pathlib import Path

CASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CASE_DIR))

from invoice_service import Invoice, InvoiceService, User


ALICE = User(id="U1", name="Alice")
BOB = User(id="U2", name="Bob")

INVOICES = [
    Invoice(id="I101", user_id="U1", amount=100.0),
    Invoice(id="I102", user_id="U2", amount=250.0),
    Invoice(id="I103", user_id="U1", amount=75.0),
]


def create_service() -> InvoiceService:
    return InvoiceService(INVOICES)


def test_standard_path_allows_owner():
    service = create_service()

    invoice = service.get_invoice("I101", ALICE)

    assert invoice is not None
    assert invoice.user_id == ALICE.id


def test_standard_path_denies_other_user():
    service = create_service()

    invoice = service.get_invoice("I102", ALICE)

    assert invoice is None


def test_alternate_path_allows_owner():
    service = create_service()

    invoice = service.get_invoice_by_reference("I101", ALICE)

    assert invoice is not None
    assert invoice.user_id == ALICE.id


def test_alternate_path_denies_other_user():
    service = create_service()

    invoice = service.get_invoice_by_reference("I102", ALICE)

    assert invoice is None


def test_nonexistent_invoice_returns_none_from_both_paths():
    service = create_service()

    standard_invoice = service.get_invoice("I999", ALICE)
    alternate_invoice = service.get_invoice_by_reference("I999", ALICE)

    assert standard_invoice is None
    assert alternate_invoice is None
