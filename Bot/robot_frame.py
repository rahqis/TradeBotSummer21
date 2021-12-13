# Last Updated: Rahqi Sarsour 4:20 PM 06/06/21

import pandas as pd

from td.client import TDClient
from td.utils import TDUtilities

from datetime import datetime as dt, timezone
from datetime import time
from datetime import timezone as tz

from typing import List, Dict, Optional, Union
from Bot.portfolio import Portfolio
from Bot.stock_frame import StockFrame
from Bot.trade import Trade


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
        pre_market_start = dt.utcnow().replace(
            hour=12, minute=00, second=00).timestamp()
        market_start = dt.utcnow().replace(hour=13, minute=30,
                                           second=00).timestamp()
        current_time = dt.utcnow().timestamp()

        if(market_start >= current_time >= pre_market_start):
            return True
        else:
            return False

    # checks after hours
    @property
    def is_after_hours(self) -> bool:
        after_hr_start = dt.utcnow().replace(
            hour=22, minute=30, second=00).timestamp()
        market_end = dt.utcnow().replace(hour=20, minute=00,
                                         second=00).timestamp()
        current_time = dt.utcnow().timestamp()

        if after_hr_start >= current_time >= market_end:
            return True
        else:
            return False

    # checks market hours
    @property
    def is_reg_open(self) -> bool:
        market_start = dt.utcnow().replace(hour=13, minute=30,
                                           second=00).timestamp()
        market_end = dt.utcnow().replace(hour=20, minute=00,
                                         second=00).timestamp()
        current_time = dt.utcnow().timestamp()

        if(market_end >= current_time >= market_start):
            return True
        else:
            return False

    def new_portfolio(self):
        self.portfolio.td_client = Portfolio(acct_num=self.acct)
        self.portfolio._td_client = self.session

    def create_trade(self, trade_id: str, enter_or_exit: str, long_or_short: str, order_type: str = 'mkt',
                     price: float = 0, stop_limit_price: float = 0):

        # init trade object
        trade = Trade()

        # create new trade
        trade.new_trade(
            trade_id=trade_id,
            enter_exit=enter_or_exit,
            long_or_short=long_or_short,
            price=price,
            stop_limit=stop_limit_price,
        )

        self.trades[trade_id] = trade

        return trade

    def new_stock_frame(self, data: List[dict]) -> StockFrame:

        self.stock_frame = StockFrame(data=data)

        return self.stock_frame

    def updated_quote(self) -> dict:
        tickers = self.portfolio.positions.keys()

        quotes = self.session.get_quotes(instruments=list(tickers))

        return quotes

    def hist_quote(self, start: dt, end: dt, bar_size: int = 1, bar_type: str = 'minute', symbols: Optional[List[str]] = None) -> List[Dict]:

        self._bar_size = bar_size
        self._bar_type = bar_type

        start = str(TDUtilities.milliseconds_since_epoch(dt_object=start))
        end = str(TDUtilities.milliseconds_since_epoch(dt_object=end))

        new_prices = []

        if not symbols:
            symbols = self.portfolio.positions

        for symbol in symbols:

            hist_price_resp = self.session.get_price_history(
                symbol=symbol,
                period_type='day',
                start_date=start,
                end_date=end,
                frequency_type=bar_type,
                frequency=bar_size,
                extended_hours=True
            )
            self.hist_prices[symbol] = {}
            self.hist_prices[symbol]['candles'] = hist_price_resp['candles']

            for candle in hist_price_resp['candles']:

                new_price_mini_dict = {}
                new_price_mini_dict['symbol'] = candle['symbol']
                new_price_mini_dict['open'] = candle['open']
                new_price_mini_dict['close'] = candle['close']
                new_price_mini_dict['high'] = candle['high']
                new_price_mini_dict['volume'] = candle['volume']
                new_price_mini_dict['datetime'] = candle['datetime']

                new_prices.append(new_price_mini_dict)

        self.hist_prices['aggregated'] = new_prices

        return self.hist_prices
