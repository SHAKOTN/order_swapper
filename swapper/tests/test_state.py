from swapper.constants import SIDE_ASK
from swapper.constants import SIDE_BID
from swapper.state import State


def test_add_orders():
    state = State()
    orders = [
        {"orderId": 1, "status": "NEW"},
        {"orderId": 2, "status": "NEW"},
    ]
    state.add_orders(orders)
    assert state.orders == {1: {"orderId": 1, "status": "NEW"}, 2: {"orderId": 2, "status": "NEW"}}


def test_get_active_orders():
    state = State()
    orders = [
        {"orderId": 1, "status": "NEW"},
        {"orderId": 2, "status": "NEW"},
    ]
    state.add_orders(orders)
    assert state.get_active_orders() == orders
    assert state.has_active_orders() is True


def test_has_active_orders():
    state = State()
    orders = [
        {"orderId": 1, "status": "NEW"},
        {"orderId": 2, "status": "NEW"},
    ]
    state.add_orders(orders)
    assert state.has_active_orders() is True


def test_has_both_bid_ask():
    state = State()
    orders = [
        {"orderId": 1, "status": "NEW", "side": SIDE_BID},
        {"orderId": 2, "status": "NEW", "side": SIDE_ASK},
    ]
    state.add_orders(orders)
    assert state.has_both_bid_ask() is True


def test_get_active_bid_order():
    state = State()
    orders = [
        {"orderId": 1, "status": "NEW", "side": SIDE_BID},
        {"orderId": 2, "status": "NEW", "side": SIDE_ASK},
    ]
    state.add_orders(orders)
    assert state.get_active_bid_order() == orders[0]


def test_get_active_ask_order():
    state = State()
    orders = [
        {"orderId": 1, "status": "NEW", "side": SIDE_BID},
        {"orderId": 2, "status": "NEW", "side": SIDE_ASK},
    ]
    state.add_orders(orders)
    assert state.get_active_ask_order() == orders[1]


def test_get_active_orders_empty():
    state = State()
    assert state.get_active_orders() == []
    assert state.has_active_orders() is False


def test_has_both_bid_ask_empty():
    state = State()
    assert state.has_both_bid_ask() is False
