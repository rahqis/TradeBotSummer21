from _typeshed import NoneType
from datetime import datetime as dt
from typing import List, Union, Optional


class Trade():

    def __init__(self) -> None:
        self.order = {}
        self.trade_id = ""
        self.order_type = ""

        self.side = ""  # Long or Short
        self.opposite_side = ""  # Self Explanatory
        self.enter_or_exit = ""
        self.opposite_enter_exit = ""

        self.order_resp = {}
        self.trigger_added = False
        self._multi_leg = False

    def new_trade(self, id: str, order_type: str, side: str, enter_exit: str, price: float = 0.00, stop_limit: float = 0.00) -> dict:

        self.trade_id = id

        self.order_types = {
            'mkt': 'MARKET',
            'lmt': 'LIMIT',
            'stop': 'STOP',
            'stop_lmt': 'STOP_LIMIT',
            'trailing_stop': 'TRAILING_STOP'
        }

        self.order_instructions = {
            'enter': {
                'long': 'BUY',
                'short': 'SELL_SHORT'
            },
            'exit': {
                'long': 'SELL',
                'short': 'BUY_TO_COVER'
            }
        }

        self.order = {
            "orderStrategyType": "SINGLE",
            "orderType": self.order_types[order_type],
            "session": "NORMAL",
            "duration": "DAY",
            "orderLegCollection": [
                {
                    "instructions": self.order_instructions[enter_exit][side],
                    "quantity": 0,
                    "instruments": {
                        "ticker": None,
                        "assetType": None
                    }
                }
            ]
        }

        if self.order['orderType'] == 'STOP':
            self.order['stopPrice'] = price
        elif self.order['orderType'] == 'LIMIT':
            self.order['price'] = price
        elif self.order['orderType'] == 'STOP_LIMIT':
            self.order['stopPrice'] = price
            self.order['price'] = stop_limit
        elif self.order['orderType'] == 'TRAILING_STOP':
            self.order['stopPriceLinkBasis'] = ""
            self.order['stopPriceLinkType'] = ""
            self.order['stopPriceOffset'] = 0.00
            self.order['stopType'] = 'STANDARD'

        self.enter_or_exit = enter_exit
        self.side = side
        self.order_type = order_type
        self.price = price

        # Store stop price Info
        if order_type == 'stop':
            self.stop_price = price
        elif order_type == 'stop_lmt':
            self.stop_price = price
            self.stop_limit_price = stop_limit
        else:
            self.stop_price = 0.00

        # Stores side info
        if self.enter_or_exit == 'enter':
            self.opposite_enter_exit = 'exit'
        elif self.enter_or_exit == 'exit':
            self.opposite_enter_exit = 'enter'

        if self.side == 'long':
            self.opposite_side = 'short'
        elif self.side == 'short':
            self.opposite_side = 'long'

        return self.order

    def get_instrument(self, ticker: str, quantity: int, asset_type: str, sub_asset_type: str = None, order_leg_id: int = 0) -> dict:

        leg = self.order['orderLegCollection']['orderLegId']
        leg['instrument']['ticker'] = ticker
        leg['instrument']['asset_Type'] = asset_type
        leg['quantity'] = quantity

        self.order_size = quantity
        self.ticker = ticker
        self.asset_Type = asset_type

        return leg

    def good_till_cancel(self, cancel_time: dt) -> None:

        self.order['duration'] = 'GOOD_TILL_CANCEL'
        self.order['cancelTime'] = cancel_time.isoformat()

    def modify_side(self, side: Optional[str], order_leg_id: int = 0) -> None:

        if side and side not in ['buy', 'sell', 'sell_short', 'buy_to_cover']:
            raise ValueError("Invalid Side")

        if side:
            self.side['orderLegCollection']['order_leg_id']['instructions'] = side.upper()
        else:
            self.side['orderLegCollection']['order_leg_id']['instructions'] = self.order_instructions[self.enter_or_exit][self.opposite_side]

    def add_box_range(self, profit_size: float = 0.00, percentage: bool = False, stop_limit: bool = False):

        if not self.trigger_added:
            self._convert_to_trigger()

        self.add_take_profit(profit_size=profit_size, percentage=percentage)

        if not stop_limit:
            self.add_stop_loss(stop_size=profit_size, percentage=percentage)
