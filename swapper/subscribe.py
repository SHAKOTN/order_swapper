import asyncio
import json
import logging
from decimal import Decimal

import websockets

from swapper.constants import SLEEP_TIME
from swapper.helpers import calculate_ask_price_based_on_spread
from swapper.helpers import calculate_bid_ask_spread
from swapper.helpers import calculate_bid_price_based_on_spread

logger = logging.getLogger(__name__)


async def subscribe(websocket: websockets.WebSocketClientProtocol):
    """
    Subscribe to the BTCUSDT 1s kline stream. Continuously listen to the websocket and calculate
    spread changes.
    """
    await websocket.send(json.dumps({
        "method": "SUBSCRIBE",
        "params": ["btcusdt@kline_1m"],
        "id": 1
    }))

    while True:
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

        logger.info(spread)
        logger.info(f"Bid price: {bid_price}")
        logger.info(f"Ask price: {ask_price}")
