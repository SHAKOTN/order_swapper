from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Optional

from swapper.constants import OrderStatus
from swapper.constants import SIDE_ASK
from swapper.constants import SIDE_BID


@dataclass
class State:
    orders: dict = field(default_factory=dict)

    def add_orders(self, orders: List[dict]) -> None:
        for order in orders:
            self.orders[order["orderId"]] = order

    def get_active_orders(self) -> Optional[List[dict]]:
        return [
            order for order in self.orders.values() if order["status"] == OrderStatus.NEW.value
        ]

    def has_active_orders(self) -> bool:
        return bool(self.get_active_orders())

    def has_both_bid_ask(self) -> bool:
        return len(self.get_active_orders()) == 2

    def get_active_bid_order(self) -> Optional[dict]:
        orders = [order for order in self.get_active_orders() if order["side"] == SIDE_BID]
        if orders:
            return orders[0]

    def get_active_ask_order(self) -> Optional[dict]:
        orders = [order for order in self.get_active_orders() if order["side"] == SIDE_ASK]
        if orders:
            return orders[0]
