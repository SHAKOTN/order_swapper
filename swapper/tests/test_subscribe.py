from typing import Optional
from unittest.mock import MagicMock

import pytest
from pytest_httpx import HTTPXMock

from swapper.subscribe import subscribe


class _ExitLoop(Exception):
    pass


async def _ws(_: Optional[dict] = None) -> None:
    return


async def _ws_recv() -> str:
    return '{"e":"kline","E":1675609847732,"s":"BTCUSDT","k":{"t":1675609800000,' \
           '"T":1675609859999,"s":"BTCUSDT","i":"1m","f":2636784741,"L":2636787507,' \
           '"o":"23171.33000000","c":"23179.43000000","h":"23180.67000000",' \
           '"l":"23167.50000000","v":"66.74750000","n":2767,"x":false,"q":"1546784.10530020",' \
           '"V":"41.71094000","Q":"966637.21078300","B":"0"}}'


@pytest.mark.asyncio
async def test_subscribe_no_orders(httpx_mock: HTTPXMock, patch_time, mocker):
    """
    Should call place_order() twice and create two new orders.
    """
    mocker.patch(
        "swapper.subscribe.get_all_orders",
        side_effect=[[], _ExitLoop("To exit the loop")],
    )
    place_order = mocker.patch(
        "swapper.subscribe.place_order",
        side_effect=[
            {"orderId": 1, "status": "NEW", "side": "BUY"},
            {"orderId": 2, "status": "NEW", "side": "SELL"},
        ],
    )
    with pytest.raises(_ExitLoop):
        await subscribe(MagicMock(send=_ws, recv=_ws_recv))
    assert place_order.call_count == 2


@pytest.mark.asyncio
async def test_subscribe_orders_at_risk(httpx_mock: HTTPXMock, patch_time, mocker):
    """
    2 existing orders at risk to be filled. Should cancel both and place 2 new orders.
    """
    mocker.patch(
        "swapper.subscribe.get_all_orders",
        side_effect=[
            [
                {"orderId": 1, "status": "NEW", "side": "BUY"},
                {"orderId": 2, "status": "NEW", "side": "SELL"},
            ],
            _ExitLoop("To exit the loop"),
        ],
    )
    order_at_risk = mocker.patch(
        "swapper.subscribe.order_at_risk",
        side_effect=[True, True],
    )
    place_order = mocker.patch(
        "swapper.subscribe.place_order",
        side_effect=[
            {"orderId": 3, "status": "NEW", "side": "BUY"},
            {"orderId": 4, "status": "NEW", "side": "SELL"},
        ],
    )
    cancel_order = mocker.patch("swapper.subscribe.cancel_order",)
    with pytest.raises(_ExitLoop):
        await subscribe(MagicMock(send=_ws, recv=_ws_recv))
    assert place_order.call_count == 2
    assert cancel_order.call_count == 2
    assert order_at_risk.call_count == 2


@pytest.mark.asyncio
async def test_subscribe_orders_not_at_risk(httpx_mock: HTTPXMock, patch_time, mocker):
    """
    2 existing orders not at risk to be filled. Should not cancel or place any new orders.
    """
    mocker.patch(
        "swapper.subscribe.get_all_orders",
        side_effect=[
            [
                {"orderId": 1, "status": "NEW", "side": "BUY"},
                {"orderId": 2, "status": "NEW", "side": "SELL"},
            ],
            _ExitLoop("To exit the loop"),
        ],
    )
    order_at_risk = mocker.patch(
        "swapper.subscribe.order_at_risk",
        side_effect=[False, False],
    )
    place_order = mocker.patch(
        "swapper.subscribe.place_order",
        side_effect=[
            {"orderId": 3, "status": "NEW", "side": "BUY"},
            {"orderId": 4, "status": "NEW", "side": "SELL"},
        ],
    )
    cancel_order = mocker.patch("swapper.subscribe.cancel_order",)
    with pytest.raises(_ExitLoop):
        await subscribe(MagicMock(send=_ws, recv=_ws_recv))
    assert place_order.call_count == 0
    assert cancel_order.call_count == 0
    assert order_at_risk.call_count == 2


@pytest.mark.asyncio
async def test_one_order_at_risk(httpx_mock: HTTPXMock, patch_time, mocker):
    """
    1 existing order at risk to be filled. Should cancel and place 1 new order.
    """
    mocker.patch(
        "swapper.subscribe.get_all_orders",
        side_effect=[
            [
                {"orderId": 1, "status": "NEW", "side": "BUY"},
                {"orderId": 2, "status": "NEW", "side": "SELL"},
            ],
            _ExitLoop("To exit the loop"),
        ],
    )
    order_at_risk = mocker.patch(
        "swapper.subscribe.order_at_risk",
        side_effect=[True, False],
    )
    place_order = mocker.patch(
        "swapper.subscribe.place_order",
        side_effect=[
            {"orderId": 3, "status": "NEW", "side": "BUY"},
            {"orderId": 4, "status": "NEW", "side": "SELL"},
        ],
    )
    cancel_order = mocker.patch("swapper.subscribe.cancel_order",)
    with pytest.raises(_ExitLoop):
        await subscribe(MagicMock(send=_ws, recv=_ws_recv))
    assert place_order.call_count == 1
    assert cancel_order.call_count == 1
    assert order_at_risk.call_count == 2
