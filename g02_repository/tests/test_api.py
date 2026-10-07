import sys

sys.path.insert(0, "g02_repository")

from api.order_api import OrderAPI


def test_api_can_create_order():
    api = OrderAPI()

    result = api.create_order(
        order_id="O4001",
        user_id="U001",
        amount=300.0,
    )

    assert result == {
        "order_id": "O4001",
        "status": "pending",
    }


def test_api_can_retrieve_order():
    api = OrderAPI()

    api.create_order(
        order_id="O4002",
        user_id="U001",
        amount=400.0,
    )

    result = api.get_order("O4002")

    assert result == {
        "order_id": "O4002",
        "user_id": "U001",
        "amount": 400.0,
        "status": "pending",
    }


def test_api_can_pay_order_successfully():
    api = OrderAPI()

    api.create_order(
        order_id="O4003",
        user_id="U001",
        amount=500.0,
    )

    result = api.pay_order("O4003")

    assert result == {
        "order_id": "O4003",
        "success": True,
    }

    assert api.get_order("O4003")["status"] == "paid"
