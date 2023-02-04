import asyncio
import logging

import websockets
from dotenv import load_dotenv

from swapper.constants import BINANCE_WS_MARKET_STREAM_URL
from swapper.subscribe import subscribe

logging.basicConfig(level=logging.INFO)


async def connect():
    async with websockets.connect(BINANCE_WS_MARKET_STREAM_URL) as websocket:
        await subscribe(websocket)


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(connect())
