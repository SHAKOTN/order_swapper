import time
from decimal import Decimal

import pytest
from httpx import HTTPStatusError
from pytest_httpx import HTTPXMock

from swapper.constants import BINANCE_REST_API_BASE_URL
from swapper.constants import SIDE_BID
from swapper.service import calculate_signature
from swapper.service import cancel_order
from swapper.service import get_all_orders
from swapper.service import place_order


@pytest.mark.asyncio
async def test_place_order(httpx_mock: HTTPXMock, patch_time):
    price = round(Decimal(100), 2)

    data = {
        "symbol": "BTCUSDT",
        "side": SIDE_BID,
        "type": "LIMIT",
        "timeInForce": "GTC",
        "quantity": 0.01,
        "price": price,
        "timestamp": str(int(time.time() * 1000)),
    }
    signature = calculate_signature(data)
    httpx_mock.add_response(
        url=f"{BINANCE_REST_API_BASE_URL}/order?signature={signature}",
        json={"orderId": 1, "status": "NEW", "side": SIDE_BID}
    )
    response = await place_order(SIDE_BID, Decimal(100))
    assert response == {"orderId": 1, "status": "NEW", "side": SIDE_BID}


@pytest.mark.asyncio
async def test_place_order_unhappy(httpx_mock: HTTPXMock, patch_time):
    price = round(Decimal(100), 2)

    data = {
        "symbol": "BTCUSDT",
        "side": SIDE_BID,
        "type": "LIMIT",
        "timeInForce": "GTC",
        "quantity": 0.01,
        "price": price,
        "timestamp": str(int(time.time() * 1000)),
    }
    signature = calculate_signature(data)
    httpx_mock.add_response(
        url=f"{BINANCE_REST_API_BASE_URL}/order?signature={signature}",
        status_code=400,
        json={"code": -2010, "msg": "Account has insufficient balance for requested action."}
    )
    with pytest.raises(HTTPStatusError):
        await place_order(SIDE_BID, Decimal(100))


@pytest.mark.asyncio
async def test_get_all_orders(httpx_mock: HTTPXMock, patch_time):
    params = {
        "symbol": "BTCUSDT",
        "timestamp": str(int(time.time() * 1000)),
        "startTime": str(int(time.time() * 1000) - 1 * 60 * 60 * 1000),
        "endTime": str(int(time.time() * 1000)),
    }
    signature = calculate_signature(params)
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    httpx_mock.add_response(
        url=f"{BINANCE_REST_API_BASE_URL}/allOrders?{query_string}&signature={signature}",
        json=[{"orderId": 1, "status": "NEW", "side": SIDE_BID}]
    )
    response = await get_all_orders()
    assert response == [{"orderId": 1, "status": "NEW", "side": SIDE_BID}]


@pytest.mark.asyncio
async def test_get_all_orders_unhappy(httpx_mock: HTTPXMock, patch_time):
    params = {
        "symbol": "BTCUSDT",
        "timestamp": str(int(time.time() * 1000)),
        "startTime": str(int(time.time() * 1000) - 1 * 60 * 60 * 1000),
        "endTime": str(int(time.time() * 1000)),
    }
    signature = calculate_signature(params)
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    httpx_mock.add_response(
        url=f"{BINANCE_REST_API_BASE_URL}/allOrders?{query_string}&signature={signature}",
        status_code=400,
        json={}
    )
    with pytest.raises(HTTPStatusError):
        await get_all_orders()


@pytest.mark.asyncio
async def test_cancel_order(httpx_mock: HTTPXMock, patch_time):
    httpx_mock.add_response(
        url="https://api.binance.com/api/v3/time",
        json={"serverTime": int(time.time() * 1000)}
    )
    params = {
        "symbol": "BTCUSDT",
        "orderId": 1,
        "timestamp": str(int(time.time() * 1000)),
        "recvWindow": 5000,
    }
    signature = calculate_signature(params)
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    httpx_mock.add_response(
        url=f"{BINANCE_REST_API_BASE_URL}/order?{query_string}&signature={signature}",
        json={"orderId": 1, "status": "CANCELED", "side": SIDE_BID}
    )
    response = await cancel_order(1)
    assert response == {"orderId": 1, "status": "CANCELED", "side": SIDE_BID}


@pytest.mark.asyncio
async def test_cancel_order_unhappy(httpx_mock: HTTPXMock, patch_time):
    httpx_mock.add_response(
        url="https://api.binance.com/api/v3/time",
        json={"serverTime": int(time.time() * 1000)}
    )
    params = {
        "symbol": "BTCUSDT",
        "orderId": 1,
        "timestamp": str(int(time.time() * 1000)),
        "recvWindow": 5000,
    }
    signature = calculate_signature(params)
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    httpx_mock.add_response(
        url=f"{BINANCE_REST_API_BASE_URL}/order?{query_string}&signature={signature}",
        status_code=400,
        json={}
    )
    response = await cancel_order(1)
    assert response is None
