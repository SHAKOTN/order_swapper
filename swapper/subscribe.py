import asyncio
import json
import logging
from decimal import Decimal

import websockets
from httpx import TimeoutException
from tenacity import retry
from tenacity import retry_if_exception_type

from swapper.constants import SIDE_ASK
from swapper.constants import SIDE_BID
from swapper.constants import SLEEP_TIME
from swapper.helpers import calculate_ask_price_based_on_spread
from swapper.helpers import calculate_bid_ask_spread
from swapper.helpers import calculate_bid_price_based_on_spread
from swapper.helpers import order_at_risk
from swapper.service import cancel_order
from swapper.service import get_all_orders
from swapper.service import place_order
from swapper.state import State

logger = logging.getLogger(__name__)


@retry(stop=asyncio.CancelledError, retry=retry_if_exception_type(TimeoutException))
async def subscribe(websocket: websockets.WebSocketClientProtocol) -> None:
    """
    Subscribe to the BTCUSDT 1s kline stream. Continuously listen to the websocket and calculate
    spread changes.

    There are several cases:
    1. There are no existing orders on the exchange. We need to place new orders for ask and bid
    2. There is one ask(or bid) order active, need to cancel it(if needed) and place a new one
    3. There are existing orders on the exchange. We need to load them to state and monitor if
        their price is getting closer to order be filled. If so, we need to cancel orders and place
        new ones
    """
    await websocket.send(json.dumps({
        "method": "SUBSCRIBE",
        "params": ["btcusdt@kline_1m"],
        "id": 1
    }))

    while True:
        # First, get all orders and load them to state
        state = State()
        orders = await get_all_orders()
        state.add_orders(orders)

        if len(state.get_active_orders()) > 2:
            # If there are more than 2 active orders, something is wrong. Let it resolve itself
            logger.error("There are more than 2 active orders. Something is wrong")
            await asyncio.sleep(SLEEP_TIME)
            continue

        klines_response = await websocket.recv()
        data = json.loads(klines_response)
        if not data or data.get('k') is None:
            # Sleep for a bit in case of a connection error
            logger.info(f"No data received from websocket. Sleeping for {SLEEP_TIME} seconds")
            await asyncio.sleep(SLEEP_TIME)
            continue
        # Calculate spread and find out the bid and ask price
        high_price = Decimal(data["k"]["h"])
        low_price = Decimal(data["k"]["l"])

        spread = calculate_bid_ask_spread(low_price, high_price)
        curr_bid_price = calculate_bid_price_based_on_spread(low_price, spread)
        curr_ask_price = calculate_ask_price_based_on_spread(high_price, spread)

        # Create two new active orders if there are no active orders
        if not state.has_active_orders():
            initial_orders_placement = await asyncio.gather(
                *[place_order(SIDE_BID, curr_bid_price),
                  place_order(SIDE_ASK, curr_ask_price)]
            )
            logger.info(
                f"Placed BID order: {initial_orders_placement[0]['orderId']} "
                f"with {curr_bid_price} price"
                f"Placed ASK order: {initial_orders_placement[0]['orderId']} "
                f"with {curr_ask_price} price"
            )
        else:
            # There are active orders. Check if they need to be cancelled and replaced
            bid_order = state.get_active_bid_order()
            if bid_order and order_at_risk(curr_bid_price, curr_ask_price, bid_order):
                logger.warning(
                    f"Bid Order {bid_order['orderId']} is close to be filled. Cancelling now!"
                )
                # Cancel the order
                await cancel_order(bid_order['orderId'])
                new_order = await place_order(SIDE_BID, curr_bid_price)
                logger.info(
                    f"Placed BID order: {new_order['orderId']} with {curr_bid_price} price"
                )
            elif not bid_order:
                new_order = await place_order(SIDE_BID, curr_bid_price)
                logger.info(
                    f"Placed BID order: {new_order['orderId']} with {curr_bid_price} price"
                )
            ask_order = state.get_active_ask_order()
            if ask_order and order_at_risk(curr_bid_price, curr_ask_price, ask_order):
                logger.warning(
                    f"Ask Order {ask_order['orderId']} is close to be filled. Cancelling now!"
                )
                # Cancel the order
                await cancel_order(ask_order['orderId'])
                new_order = await place_order(SIDE_ASK, curr_ask_price)
                logger.info(
                    f"Placed ASK order: {new_order['orderId']} with {curr_ask_price} price"
                )
            elif not ask_order:
                new_order = await place_order(SIDE_ASK, curr_ask_price)
                logger.info(
                    f"Placed ASK order: {new_order['orderId']} with {curr_ask_price} price"
                )
        # await asyncio.sleep(SLEEP_TIME)
