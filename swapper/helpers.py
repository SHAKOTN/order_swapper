from decimal import Decimal


def calculate_bid_ask_spread(low_price: Decimal, high_price: Decimal) -> Decimal:
    """
    Calculate the bid/ask spread for BTCUSDT.
    """
    return Decimal((high_price - low_price) / low_price * 100)


def calculate_bid_price_based_on_spread(low_price: Decimal, spread: Decimal) -> Decimal:
    """
    Calculate the bid price based on the spread.
    """
    return Decimal(low_price * (1 - spread / 100))


def calculate_ask_price_based_on_spread(high_price: Decimal, spread: Decimal) -> Decimal:
    """
    Calculate the ask price based on the spread.
    """
    return Decimal(high_price * (1 + spread / 100))
