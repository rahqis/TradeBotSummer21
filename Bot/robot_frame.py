# Last Updated: Rahqi Sarsour 4:20 PM 06/06/21

from os import stat_result
import pandas as pd
import pathlib
import json

import time as time_true
from td.client import TDClient
from td.utils import TDUtilities

from datetime import datetime as dt, timezone, tzinfo
from datetime import time
from datetime import timezone as tz
from datetime import timedelta
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

    def get_latest_bar(self) -> List[dict]:

        bar_size = self._bar_size
        bar_type = self._bar_type

        # date range
        end_date = dt.today()
        start_date = end_date - timedelta(minutes=15)

        start = str(TDUtilities.milliseconds_since_epoch(dt_object=start_date))
        end = str(TDUtilities.milliseconds_since_epoch(dt_object=end_date))

        latest_prices = []

        for symbol in self.portfolio.positions:

            hist_price_resp = self.session.get_price_history(
                symbol=symbol,
                period_type='day',
                start_date=start,
                end_date=end,
                frequency_type=bar_type,
                frequency=bar_size,
                extended_hours=True
            )

            if 'error' in hist_price_resp:
                time_true.sleep(2)

                hist_price_resp = self.session.get_price_history(
                    symbol=symbol,
                    period_type='day',
                    start_date=start,
                    end_date=end,
                    frequency_type=bar_type,
                    frequency=bar_size,
                    extended_hours=True
                )

            for candle in hist_price_resp['candles'][-1:]:

                new_price_mini_dict = {}
                new_price_mini_dict['symbol'] = candle['symbol']
                new_price_mini_dict['open'] = candle['open']
                new_price_mini_dict['close'] = candle['close']
                new_price_mini_dict['high'] = candle['high']
                new_price_mini_dict['volume'] = candle['volume']
                new_price_mini_dict['datetime'] = candle['datetime']

                latest_prices.append(new_price_mini_dict)

        return latest_prices

    def wait_till_next_bar(self, last_bar_timestap: pd.DatetimeIndex) -> None:

        last_bar = last_bar_timestap.to_pydatetime()[
            0].replace(tzinfo=timezone.utc)

        next_bar = last_bar_timestap+timedelta(seconds=60)

        curr_bar_time = dt.now(tz=timezone.utc)

        last_bar_timestamp = int(last_bar.timestamp())
        next_bar_timestamp = int(next_bar.timestamp())
        curr_bar_timestamp = int(curr_bar_time.timestamp())

        _time_to_wait_bar = next_bar_timestamp-last_bar_timestamp

        time_to_wait_now = next_bar_timestamp - curr_bar_time

        if time_to_wait_now < 0:
            time_to_wait_now = 0

        print("=" * 80)
        print("Pausing for the next bar")
        print("-" * 80)
        print("Curr Time: {time_curr}".format(
            time_curr=curr_bar_time.strftime("%Y-%m-%d %H:%M:%S")
        )
        )
        print("Next Time: {time_next}".format(
            time_next=next_bar_time.strftime("%Y-%m-%d %H:%M:%S")
        )
        )
        print("Sleep Time: {seconds}".format(seconds=time_to_wait_now))
        print("-" * 80)
        print('')

        time_true.sleep(time_to_wait_now)

    def execute_signals(self, signals: List[pd.Series], trades_to_execute: dict) -> List[dict]:
        """Executes the specified trades for each signal.
        Arguments:
        ----
        signals {list} -- A pandas.Series object representing the buy signals and sell signals.
            Will check if series is empty before making any trades.
        Trades:
        ----
        trades_to_execute {dict} -- the trades you want to execute if signals are found.
        Returns:
        ----
        {List[dict]} -- Returns all order responses.
        Usage:
        ----
            >>> trades_dict = {
                    'MSFT': {
                        'trade_func': trading_robot.trades['long_msft'],
                        'trade_id': trading_robot.trades['long_msft'].trade_id
                    }
                }
            >>> signals = indicator_client.check_signals()
            >>> trading_robot.execute_signals(
                    signals=signals,
                    trades_to_execute=trades_dict
                )
        """

        # Define the Buy and sells.
        buys: pd.Series = signals['buys']
        sells: pd.Series = signals['sells']

        order_responses = []

        # If we have buys or sells continue.
        if not buys.empty:

            # Grab the buy Symbols.
            symbols_list = buys.index.get_level_values(0).to_list()

            # Loop through each symbol.
            for symbol in symbols_list:

                # Check to see if there is a Trade object.
                if symbol in trades_to_execute:

                    if self.portfolio.in_portfolio(symbol=symbol):
                        self.portfolio.set_ownership_status(
                            symbol=symbol,
                            ownership=True
                        )

                    # Set the Execution Flag.
                    trades_to_execute[symbol]['has_executed'] = True
                    trade_obj: Trade = trades_to_execute[symbol]['buy']['trade_func']

                    if not self.paper_trading:

                        # Execute the order.
                        order_response = self.execute_orders(
                            trade_obj=trade_obj
                        )

                        order_response = {
                            'order_id': order_response['order_id'],
                            'request_body': order_response['request_body'],
                            'timestamp': datetime.now().isoformat()
                        }

                        order_responses.append(order_response)

                    else:

                        order_response = {
                            'order_id': trade_obj._generate_order_id(),
                            'request_body': trade_obj.order,
                            'timestamp': datetime.now().isoformat()
                        }

                        order_responses.append(order_response)

        elif not sells.empty:

            # Grab the buy Symbols.
            symbols_list = sells.index.get_level_values(0).to_list()

            # Loop through each symbol.
            for symbol in symbols_list:

                # Check to see if there is a Trade object.
                if symbol in trades_to_execute:

                    # Set the Execution Flag.
                    trades_to_execute[symbol]['has_executed'] = True

                    if self.portfolio.in_portfolio(symbol=symbol):
                        self.portfolio.set_ownership_status(
                            symbol=symbol,
                            ownership=False
                        )

                    trade_obj: Trade = trades_to_execute[symbol]['sell']['trade_func']

                    if not self.paper_trading:

                        # Execute the order.
                        order_response = self.execute_orders(
                            trade_obj=trade_obj
                        )

                        order_response = {
                            'order_id': order_response['order_id'],
                            'request_body': order_response['request_body'],
                            'timestamp': datetime.now().isoformat()
                        }

                        order_responses.append(order_response)

                    else:

                        order_response = {
                            'order_id': trade_obj._generate_order_id(),
                            'request_body': trade_obj.order,
                            'timestamp': datetime.now().isoformat()
                        }

                        order_responses.append(order_response)

        # Save the response.
        self.save_orders(order_response_dict=order_responses)

        return order_responses

    def execute_orders(self, trade_obj: Trade) -> dict:
        """Executes a Trade Object.
        Overview:
        ----
        The `execute_orders` method will execute trades as they're signaled. When executed,
        the `Trade` object will have the order response saved to it, and the order response will
        be saved to a JSON file for further analysis.
        Arguments:
        ----
        trade_obj {Trade} -- A trade object with the `order` property filled out.
        Returns:
        ----
        {dict} -- An order response dicitonary.
        """

        # Execute the order.
        order_dict = self.session.place_order(
            account=self.trading_account,
            order=trade_obj.order
        )

        # Store the order.
        trade_obj._order_response = order_dict

        # Process the order response.
        trade_obj._process_order_response()

        return order_dict

    def save_orders(self, order_response_dict: dict) -> bool:
        """Saves the order to a JSON file for further review.
        Arguments:
        ----
        order_response {dict} -- A single order response.
        Returns:
        ----
        {bool} -- `True` if the orders were successfully saved.
        """

        def default(obj):

            if isinstance(obj, bytes):
                return str(obj)

        # Define the folder.
        folder: pathlib.PurePath = pathlib.Path(
            __file__
        ).parents[1].joinpath("data")

        # See if it exist, if not create it.
        if not folder.exists():
            folder.mkdir()

        # Define the file path.
        file_path = folder.joinpath('orders.json')

        # First check if the file alread exists.
        if file_path.exists():
            with open('data/orders.json', 'r') as order_json:
                orders_list = json.load(order_json)
        else:
            orders_list = []

        # Combine both lists.
        orders_list = orders_list + order_response_dict

        # Write the new data back.
        with open(file='data/orders.json', mode='w+') as order_json:
            json.dump(obj=orders_list, fp=order_json,
                      indent=4, default=default)

        return True
