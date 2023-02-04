import asyncio
import json
import logging
from decimal import Decimal

import websockets

from swapper.constants import SIDE_ASK
from swapper.constants import SIDE_BID
from swapper.constants import SLEEP_TIME
from swapper.helpers import calculate_ask_price_based_on_spread
from swapper.helpers import calculate_bid_ask_spread
from swapper.helpers import calculate_bid_price_based_on_spread
from swapper.service import get_all_orders
from swapper.service import place_order

logger = logging.getLogger(__name__)


async def subscribe(websocket: websockets.WebSocketClientProtocol):
    """
    Subscribe to the BTCUSDT 1s kline stream. Continuously listen to the websocket and calculate
    spread changes.
    """
    active_orders = {}
    await websocket.send(json.dumps({
        "method": "SUBSCRIBE",
        "params": ["btcusdt@kline_1m"],
        "id": 1
    }))

    while True:
        # First, get all orders and load them to state
        orders = await get_all_orders()
        for order in orders:
            active_orders[order["orderId"]] = order
        response = await websocket.recv()
        data = json.loads(response)
        logger.info(data)
        if not data or data.get('k') is None:
            # Sleep for a bit in case of a connection error
            await asyncio.sleep(SLEEP_TIME)
            logger.info(f"Sleeping for {SLEEP_TIME} seconds")
            continue
        # Calculate spread
        high_price = Decimal(data["k"]["h"])
        low_price = Decimal(data["k"]["l"])
        spread = calculate_bid_ask_spread(low_price, high_price)

        bid_price = calculate_bid_price_based_on_spread(low_price, spread)
        ask_price = calculate_ask_price_based_on_spread(high_price, spread)
        if not active_orders:
            bid_order = await place_order(SIDE_BID, bid_price)
            logger.info(f"Placed order: {bid_order['orderId']} with {bid_price} price")
            ask_order = await place_order(SIDE_ASK, ask_price)
            logger.info(f"Placed order: {ask_order['orderId']} with {ask_price} price")
            logger.info(f"Spread: {spread}")

