from enum import Enum

BINANCE_WS_MARKET_STREAM_URL = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"  # Production ws
BINANCE_REST_API_BASE_URL = "https://testnet.binance.vision/api/v3"  # Testnet API

# Misc
SLEEP_TIME = 5

# Trades
ORDER_TYPE = "LIMIT"
SYMBOL = "BTCUSDT"
SIDE_BID = "BUY"
SIDE_ASK = "SELL"
TIME_IN_FORCE = "GTC"
QUANTITY = 0.01


class OrderStatus(Enum):
    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    PENDING_CANCEL = "PENDING_CANCEL"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
