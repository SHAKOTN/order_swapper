from decimal import Decimal

import pytest

from swapper.constants import SIDE_ASK
from swapper.constants import SIDE_BID
from swapper.helpers import calculate_ask_price_based_on_spread
from swapper.helpers import calculate_bid_ask_spread
from swapper.helpers import calculate_bid_price_based_on_spread
from swapper.helpers import order_at_risk


def test_calculate_bid_ask_spread():
    assert calculate_bid_ask_spread(Decimal("10000"), Decimal("10010")) == Decimal("0.1")
    assert calculate_bid_ask_spread(Decimal("10000"), Decimal("10020")) == Decimal("0.2")


def test_calculate_bid_ask_spread_with_negative_values():
    with pytest.raises(ValueError) as err:
        calculate_bid_ask_spread(Decimal("-10000"), Decimal("10010"))

    assert err.value.args[0] == "Prices cannot be negative"


def test_calculate_bid_price_based_on_spread():
    assert calculate_bid_price_based_on_spread(Decimal("10000"), Decimal("0.1")) == Decimal("9990")
    assert calculate_bid_price_based_on_spread(Decimal("10000"), Decimal("0.2")) == Decimal("9980")


def test_calculate_bid_price_based_on_spread_with_negative_values():
    with pytest.raises(ValueError) as err:
        calculate_bid_price_based_on_spread(Decimal("-10000"), Decimal("0.1"))

    assert err.value.args[0] == "Prices and spread cannot be negative"


def test_calculate_ask_price_based_on_spread():
    assert calculate_ask_price_based_on_spread(Decimal("10000"), Decimal("0.1")) == Decimal("10010")
    assert calculate_ask_price_based_on_spread(Decimal("10000"), Decimal("0.2")) == Decimal("10020")


def test_calculate_ask_price_based_on_spread_with_negative_values():
    with pytest.raises(ValueError) as err:
        calculate_ask_price_based_on_spread(Decimal("-10000"), Decimal("0.1"))

    assert err.value.args[0] == "Prices and spread cannot be negative"


def test_order_at_risk():
    assert order_at_risk(
        bid_price=Decimal("10000"), ask_price=Decimal("10010"),
        order={"side": SIDE_BID, "price": "10000"}
    )
    assert order_at_risk(
        bid_price=Decimal("10000"), ask_price=Decimal("10010"),
        order={"side": SIDE_ASK, "price": "10010"}
    )
    assert not order_at_risk(
        bid_price=Decimal("10000"), ask_price=Decimal("10010"),
        order={"side": SIDE_BID, "price": "10001"}
    )
    assert not order_at_risk(
        bid_price=Decimal("10000"), ask_price=Decimal("10010"),
        order={"side": SIDE_ASK, "price": "10009"}
    )


def test_order_at_risk_with_negative_values():
    with pytest.raises(ValueError) as err:
        order_at_risk(
            bid_price=Decimal("-10000"), ask_price=Decimal("10010"),
            order={"side": SIDE_BID, "price": "10000"}
        )

    assert err.value.args[0] == "Prices cannot be negative"
