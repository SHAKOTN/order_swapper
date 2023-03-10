"""
Module that interacts with Binance API
"""
import hashlib
import hmac
import logging
import os
import time
from decimal import Decimal
from typing import List
from typing import Optional
from typing import Union

import httpx

from swapper.constants import BINANCE_REST_API_BASE_URL
from swapper.constants import BINANCE_TIME_API_URL
from swapper.constants import ORDER_TYPE
from swapper.constants import QUANTITY
from swapper.constants import SIDE_ASK
from swapper.constants import SIDE_BID
from swapper.constants import SYMBOL
from swapper.constants import TIME_IN_FORCE

SECRET_KEY = os.getenv("SECRET_KEY")
API_KEY = os.getenv("API_KEY")

HEADERS = {
    "X-MBX-APIKEY": API_KEY,
    "Content-Type": "application/x-www-form-urlencoded",
}

logger = logging.getLogger(__name__)


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
    # Build the request body
    data = {
        "symbol": SYMBOL,
        "side": side,
        "type": ORDER_TYPE,
        "timeInForce": TIME_IN_FORCE,
        "quantity": QUANTITY,
        "price": round(price, 2),
        "timestamp": str(int(time.time() * 1000)),
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BINANCE_REST_API_BASE_URL}/order",
            # Send the signature as a query param
            params={"signature": calculate_signature(data)},
            headers=HEADERS,
            data=data
        )
        # TODO: Better error handling
        response.raise_for_status()

    return response.json()


async def get_all_orders() -> List[dict]:
    """
    Get all orders from Binance
    """
    # Build the request body
    params = {
        "symbol": SYMBOL,
        "timestamp": str(int(time.time() * 1000)),
        # Get all orders from the last 1 hour
        "startTime": str(int(time.time() * 1000) - 1 * 60 * 60 * 1000),
        "endTime": str(int(time.time() * 1000)),
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BINANCE_REST_API_BASE_URL}/allOrders",
            # Send the signature as a query param
            params={**params, "signature": calculate_signature(params)},
            headers=HEADERS,
        )
        response.raise_for_status()
    return response.json()


async def cancel_order(order_id: int) -> Optional[dict]:
    """
    Cancel an order from Binance
    :param order_id: The order ID
    """
    # Get Binance server time to avoid timestamp errors
    async with httpx.AsyncClient() as client:
        time_response = await client.get(BINANCE_TIME_API_URL)
        if time_response.status_code == 200:
            timestamp = time_response.json()["serverTime"]
        else:
            timestamp = str(int(time.time() * 1000))

    # Build the request body
    params = {
        "symbol": SYMBOL,
        "orderId": order_id,
        "timestamp": timestamp,
        "recvWindow": 5000,
    }
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{BINANCE_REST_API_BASE_URL}/order",
            # Send the signature as a query param
            params={**params, "signature": calculate_signature(params)},
            headers=HEADERS,
        )
        if response.status_code == 200:
            logger.info(f"Order {order_id} cancelled successfully")
        else:
            logger.error(f"Error cancelling order {order_id}: {response.json()}")
            return

    return response.json()
