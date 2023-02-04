"""
Module that interacts with Binance API
"""
import hashlib
import hmac
import os
from decimal import Decimal
from typing import Union

import httpx

from swapper.constants import BINANCE_REST_API_BASE_URL
from swapper.constants import ORDER_TYPE
from swapper.constants import QUANTITY
from swapper.constants import SIDE_ASK
from swapper.constants import SIDE_BID
from swapper.constants import SYMBOL
from swapper.constants import TIME_IN_FORCE

SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")


def calculate_signature(data: dict) -> str:
    """
    Calculate the signature for a request to Binance
    :param data: The request body
    :return: The signature
    """

    query_string = "&".join([f"{k}={v}" for k, v in data.items()])
    signature = hmac.new(SECRET_KEY.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256)
    return signature.hexdigest()


async def place_order(side: Union[SIDE_BID, SIDE_ASK], price: Decimal) -> dict:
    """
    Place an order on Binance
    :param side: The side of the order, either "BUY" or "SELL"
    :param price: The price of the order
    """
    api_key = os.getenv("BINANCE_API_KEY")
    # Build the request body
    data = {
        "symbol": SYMBOL,
        "side": side,
        "type": ORDER_TYPE,
        "timeInForce": TIME_IN_FORCE,
        "quantity": QUANTITY,
        "price": price
    }
    headers = {
        "X-MBX-APIKEY": api_key,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BINANCE_REST_API_BASE_URL}/order",
            # Send the signature as a query param
            params={"signature": calculate_signature(data)},
            headers=headers,
            data=data
        )
        # TODO: Better error handling
        response.raise_for_status()

    return response.json()
