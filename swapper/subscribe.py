import json
import logging

import websockets


logger = logging.getLogger(__name__)


class NoDataReceivedFromWebsocket(Exception):
    pass


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
        if not data:
            raise NoDataReceivedFromWebsocket("No data received from websocket")
        logger.info(data)
