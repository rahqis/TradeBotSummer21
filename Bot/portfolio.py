# Last Updated: Rahqi Sarsour 8:32 PM 06/08/21

from td.client import TDClient
from typing import List, Dict, Tuple, Union, Optional
from typing import TYPE_CHECKING

from os import PathLike
StrOrBytesPath = Union[str, bytes, PathLike[str], PathLike[bytes]]


class Portfolio():

    def __init__(self, acct_num: Optional[str]) -> None:

        self.positions = {}
        self.position_count = 0
        self.market_val = 0.0
        self.profit = 0.0
        self.risk_tolerance = 0.0
        self.acct_num = acct_num
        self._td_client: TDClient = None

    def new_position(self, ticker: str, asset_type: str, purchase_date: Optional[str], quantity: int = 0, price: float = 0.0) -> dict:

        self.positions[ticker] = {}
        self.positions[ticker]['ticker'] = ticker
        self.positions[ticker]['quantity'] = quantity
        self.positions[ticker]['price'] = price
        self.positions[ticker]['purchase_date'] = purchase_date
        self.positions[ticker]['asset_type'] = asset_type

        return self.positions

    def new_position_collection(self, positions: List[dict]) -> dict:

        if isinstance(positions, list):
            for position in positions:
                self.new_position(
                    ticker=position['ticker'],
                    asset_type=position['asset_type'],
                    purchase_date=position.get('purchase_date', None),
                    price=position.get('price', 0.0),
                    quantity=position.get('quantity', 0)
                )

            return self.positions
        else:
            raise TypeError("Must be List of Dictionaries")

    def delete_position(self, ticker: StrOrBytesPath) -> Tuple[bool, str]:

        if ticker in self.positions:
            del self.positions[ticker]
            return (True, "{Ticker} was deleted".format(Ticker=ticker))
        else:
            return (False, "{Ticker} does not exist".format(Ticker=ticker))

    def in_portfolio(self, ticker: str) -> bool:

        if ticker in self.positions:
            return True

        return False

    def is_profitable(self, ticker: str, current_price: float) -> bool:

        # Grabs purchase price
        price = self.positions[ticker]['price']

        if (price <= current_price):
            return True

        return False

    @property  # td_client property getter method
    def td_client(self) -> TDClient:
        return self._td_client

    @td_client.setter  # td_client property setter method
    def td_client(self, td_client: TDClient) -> None:
        self._td_client: TDClient = td_client

    def total_allocation(self):
        pass

    def risk_exposure(self):
        pass

    def total_market_val(self):
        pass
