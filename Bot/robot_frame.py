# Last Updated: Rahqi Sarsour 4:20 PM 06/06/21

import pandas as pd

from td.client import TDClient
from td.utils import TDUtilities

from datetime import datetime as dt, timezone
from datetime import time
from datetime import timezone as tz

from typing import List, Dict, Union
from Bot.portfolio import Portfolio


class robotFrame():

    def __init__(self, client_id: str, redirect_uri: str, creds: str = None, acct: str = None, paper_trading: bool = True) -> None:

        self.acct: str = acct
        self.client_id: str = client_id
        self.redirect_uri: str = redirect_uri
        self.creds: str = creds
        self.session: TDClient = self.__new_session()
        self.trades: dict = {}
        self.hist_prices: dict = {}
        self.stock_frame = None
        self.paper_trading = paper_trading
        self.portfolio: Portfolio = None

    def __new_session(self) -> TDClient:

        td_client = TDClient(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            credentials_path=self.creds
        )

        td_client.login()

        return td_client

    # checks pre market hour
    @property
    def is_pre_market(self) -> bool:
        pre_market_start = dt.now().replace(
            hour=12, minute=00, second=00, tzinfo=tz.utc).timestamp()
        market_start = dt.now().replace(hour=13, minute=30,
                                        second=00, tzinfo=tz.utc).timestamp()
        current_time = dt.now().replace(tzinfo=tz.utc).timestamp()

        if(market_start >= current_time >= pre_market_start):
            return True
        else:
            return False

    # checks after hours
    @property
    def is_after_hours(self) -> bool:
        after_hr_start = dt.now().replace(
            hour=22, minute=30, second=00, tzinfo=tz.utc).timestamp()
        market_end = dt.now().replace(hour=20, minute=00,
                                      second=00, tzinfo=tz.utc).timestamp()
        current_time = dt.now().replace(tzinfo=tz.utc).timestamp()

        if after_hr_start >= current_time >= market_end:
            return True
        else:
            return False

    # checks market hours
    @property
    def is_reg_open(self) -> bool:
        market_start = dt.now().replace(hour=13, minute=30,
                                        second=00, tzinfo=tz.utc).timestamp()
        market_end = dt.now().replace(hour=20, minute=00,
                                      second=00, tzinfo=tz.utc).timestamp()
        current_time = dt.now().replace(tzinfo=tz.utc).timestamp()

        if(market_end >= current_time >= market_start):
            return True
        else:
            return False

    def new_portfolio(self):
        self.portfolio.td_client = Portfolio(acct_num=self.acct)
        self.portfolio._td_client = self.session

    def new_trade(self):
        pass

    def new_stock_frame(self):
        pass

    def updated_quote(self) -> dict:
        tickers = self.portfolio.positions.keys()

        quotes = self.session.get_quotes(instruments=list(tickers))

        return quotes

    def hist_quote(self) -> List[Dict]:
        pass
