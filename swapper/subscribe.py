import asyncio
import json
import logging
from decimal import Decimal

import websockets

from swapper.constants import OrderStatus
from swapper.constants import SIDE_ASK
from swapper.constants import SIDE_BID
from swapper.constants import SLEEP_TIME
from swapper.helpers import calculate_ask_price_based_on_spread
from swapper.helpers import calculate_bid_ask_spread
from swapper.helpers import calculate_bid_price_based_on_spread
from swapper.service import get_all_orders
from swapper.service import place_order
from swapper.state import State

logger = logging.getLogger(__name__)


async def subscribe(websocket: websockets.WebSocketClientProtocol) -> None:
    """
    Subscribe to the BTCUSDT 1s kline stream. Continuously listen to the websocket and calculate
    spread changes.

    There are several cases:
    1. There are existing orders on the exchange. We need to load them to state and monitor if
        their price changes by more than the spread. If so, we need to cancel orders and place
        new ones
    2. There is one ask(or bid) order active, need to cancel it(if needed) and place a new one
    3. There are no existing orders on the exchange. We need to place new orders for ask and bid
    """
    state = State()
    await websocket.send(json.dumps({
        "method": "SUBSCRIBE",
        "params": ["btcusdt@kline_1m"],
        "id": 1
    }))

    while True:
        # First, get all orders and load them to state
        orders = await get_all_orders()
        for order in orders:
            if order['status'] == OrderStatus.NEW.value:
                state.add_order(order)
            # If the order is filled, cancelled, rejected or expired: remove it from state
            else:
                state.remove_inactive_order(order['orderId'])

        response = await websocket.recv()
        data = json.loads(response)
        logger.info(data)
        if not data or data.get('k') is None:
            # Sleep for a bit in case of a connection error
            logger.info(f"Sleeping for {SLEEP_TIME} seconds")
            await asyncio.sleep(SLEEP_TIME)
            continue
        # Calculate spread and find out the bid and ask price
        high_price = Decimal(data["k"]["h"])
        low_price = Decimal(data["k"]["l"])
        spread = calculate_bid_ask_spread(low_price, high_price)

        bid_price = calculate_bid_price_based_on_spread(low_price, spread)
        ask_price = calculate_ask_price_based_on_spread(high_price, spread)
        logger.info(f"Spread: {spread}")
        # Create two new active orders if there are no active orders
        if not state.has_active_orders():
            bid_order = await place_order(SIDE_BID, bid_price)
            logger.info(f"Placed order: {bid_order['orderId']} with {bid_price} price")
            ask_order = await place_order(SIDE_ASK, ask_price)
            logger.info(f"Placed order: {ask_order['orderId']} with {ask_price} price")
        elif state.has_both_bid_ask():
            # Check if order price changed too much so we have to cancel and place new orders
            active_orders = state.get_active_orders()
            for order in active_orders:
                pass
        elif state.get_active_ask_order():
            # Check if ask order price changed to much, cancel and place new one
            pass
        elif state.get_active_bid_order():
            # Check if bid order price changed to much, cancel and place new one
            pass
