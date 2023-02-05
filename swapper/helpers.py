from decimal import Decimal
from typing import Optional

from swapper.constants import SIDE_ASK
from swapper.constants import SIDE_BID


def calculate_bid_ask_spread(low_price: Decimal, high_price: Decimal) -> Decimal:
    """
    Calculate the bid/ask spread for BTCUSDT.
    """
    # Make sure prices are not negative
    if low_price < 0 or high_price < 0:
        raise ValueError("Prices cannot be negative")
    return Decimal((high_price - low_price) / low_price * 100)


def calculate_bid_price_based_on_spread(low_price: Decimal, spread: Decimal) -> Decimal:
    """
    Calculate the bid price based on the spread. Should be lower than the price
    """
    # Make sure prices and spread are not negative
    if low_price < 0 or spread < 0:
        raise ValueError("Prices and spread cannot be negative")
    return Decimal(low_price * (1 - spread / 100))


def calculate_ask_price_based_on_spread(high_price: Decimal, spread: Decimal) -> Decimal:
    """
    Calculate the ask price based on the spread. Should be higher than the price
    """
    # Make sure prices and spread are not negative
    if high_price < 0 or spread < 0:
        raise ValueError("Prices and spread cannot be negative")
    return Decimal(high_price * (1 + spread / 100))


def order_at_risk(
        bid_price: Optional[Decimal], ask_price: Optional[Decimal], order: dict
) -> bool:
    """
    Check if the order is close to be filled.

    TODO: Can make this more efficient by checking if the order is within the spread or
    use threshold
    """
    # Check prices are not negative
    if bid_price < 0 or ask_price < 0:
        raise ValueError("Prices cannot be negative")
    if order["side"] == SIDE_BID:
        return Decimal(order["price"]) <= bid_price
    if order["side"] == SIDE_ASK:
        return Decimal(order["price"]) >= ask_price
    return False
