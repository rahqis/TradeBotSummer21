import numpy as np
import pandas as pd

from typing import Any
from typing import Dict
from typing import Union

from Bot.stock_frame import StockFrame


class Indicators():

    """
    Represents an Indicator Object which can be used
    to easily add technical indicators to a StockFrame.
    """

    def __init__(self, price_data_frame: StockFrame) -> None:
        """Initalizes the Indicator Client.
        Arguments:
        ----
        price_data_frame {pyrobot.StockFrame} -- The price data frame which is used to add indicators to.
            At a minimum this data frame must have the following columns: `['timestamp','close','open','high','low']`.

        Usage:
        ----
            >>> historical_prices_df = trading_robot.grab_historical_prices(
                start=start_date,
                end=end_date,
                bar_size=1,
                bar_type='minute'
            )
            >>> price_data_frame = pd.DataFrame(data=historical_prices)
            >>> indicator_client = Indicators(price_data_frame=price_data_frame)
            >>> indicator_client.price_data_frame
        """

        self._stock_frame: StockFrame = price_data_frame
        self._price_groups = price_data_frame.symbol_groups
        self._current_indicators = {}
        self._indicator_signals = {}
        self._frame = self._stock_frame.frame

        self._indicators_comp_key = []
        self._indicators_key = []

        if self.is_multi_index:
            True

    def get_indicator_signal(self, indicator: str = None) -> Dict:
        """Return the raw Pandas Dataframe Object.
        Arguments:
        ----
        indicator {Optional[str]} -- The indicator key, for example `ema` or `sma`.
        Returns:
        ----
        {dict} -- Either all of the indicators or the specified indicator.
        """

        if indicator and indicator in self._indicator_signals:
            return self._indicator_signals[indicator]
        else:
            return self._indicator_signals

    def set_indicator_signal(self, indicator: str, buy: float, sell: float, condition_buy: Any, condition_sell: Any,
                             buy_max: float = None, sell_max: float = None, condition_buy_max: Any = None, condition_sell_max: Any = None) -> None:
        """Used to set an indicator where one indicator crosses above or below a certain numerical threshold.
        Arguments:
        ----
        indicator {str} -- The indicator key, for example `ema` or `sma`.
        buy {float} -- The buy signal threshold for the indicator.

        sell {float} -- The sell signal threshold for the indicator.
        condition_buy {str} -- The operator which is used to evaluate the `buy` condition. For example, `">"` would
            represent greater than or from the `operator` module it would represent `operator.gt`.

        condition_sell {str} -- The operator which is used to evaluate the `sell` condition. For example, `">"` would
            represent greater than or from the `operator` module it would represent `operator.gt`.
        buy_max {float} -- If the buy threshold has a maximum value that needs to be set, then set the `buy_max` threshold.
            This means if the signal exceeds this amount it WILL NOT PURCHASE THE INSTRUMENT. (defaults to None).

        sell_max {float} -- If the sell threshold has a maximum value that needs to be set, then set the `buy_max` threshold.
            This means if the signal exceeds this amount it WILL NOT SELL THE INSTRUMENT. (defaults to None).
        condition_buy_max {str} -- The operator which is used to evaluate the `buy_max` condition. For example, `">"` would
            represent greater than or from the `operator` module it would represent `operator.gt`. (defaults to None).

        condition_sell_max {str} -- The operator which is used to evaluate the `sell_max` condition. For example, `">"` would
            represent greater than or from the `operator` module it would represent `operator.gt`. (defaults to None).
        """

        # Add the key if it doesn't exist.
        if indicator not in self._indicator_signals:
            self._indicator_signals[indicator] = {}
            self._indicators_key.append(indicator)

        # Add the signals.
        self._indicator_signals[indicator]['buy'] = buy
        self._indicator_signals[indicator]['sell'] = sell
        self._indicator_signals[indicator]['buy_operator'] = condition_buy
        self._indicator_signals[indicator]['sell_operator'] = condition_sell

        # Add the max signals
        self._indicator_signals[indicator]['buy_max'] = buy_max
        self._indicator_signals[indicator]['sell_max'] = sell_max
        self._indicator_signals[indicator]['buy_operator_max'] = condition_buy_max
        self._indicator_signals[indicator]['sell_operator_max'] = condition_sell_max

    def set_indicator_signal_compare(self, indicator_1: str, indicator_2: str, condition_buy: Any, condition_sell: Any) -> None:
        """Used to set an indicator where one indicator is compared to another indicator.
        Overview:
        ----
        Some trading strategies depend on comparing one indicator to another indicator.
        For example, the Simple Moving Average crossing above or below the Exponential
        Moving Average. This will be used to help build those strategies that depend
        on this type of structure.
        Arguments:
        ----
        indicator_1 {str} -- The first indicator key, for example `ema` or `sma`.
        indicator_2 {str} -- The second indicator key, this is the indicator we will compare to. For example,
            is the `sma` greater than the `ema`.
        condition_buy {str} -- The operator which is used to evaluate the `buy` condition. For example, `">"` would
            represent greater than or from the `operator` module it would represent `operator.gt`.

        condition_sell {str} -- The operator which is used to evaluate the `sell` condition. For example, `">"` would
            represent greater than or from the `operator` module it would represent `operator.gt`.
        """

        # Define the key.
        key = "{ind_1}_comp_{ind_2}".format(
            ind_1=indicator_1,
            ind_2=indicator_2
        )

        # Add the key if it doesn't exist.
        if key not in self._indicator_signals:
            self._indicator_signals[key] = {}
            self._indicators_comp_key.append(key)

        # Grab the dictionary.
        indicator_dict = self._indicator_signals[key]

        # Add the signals.
        indicator_dict['type'] = 'comparison'
        indicator_dict['indicator_1'] = indicator_1
        indicator_dict['indicator_2'] = indicator_2
        indicator_dict['buy_operator'] = condition_buy
        indicator_dict['sell_operator'] = condition_sell

    @property
    def price_data_frame(self) -> pd.DataFrame:
        """Return the raw Pandas Dataframe Object.
        Returns:
        ----
        {pd.DataFrame} -- A multi-index data frame.
        """

        return self._frame

    @price_data_frame.setter
    def price_data_frame(self, price_data_frame: pd.DataFrame) -> None:
        """Sets the price data frame.
        Arguments:
        ----
        price_data_frame {pd.DataFrame} -- A multi-index data frame.
        """

        self._frame = price_data_frame

    def rsi(self, period: int, method: str = 'wilders', column_name: str = 'rsi') -> pd.DataFrame:
        """Calculates the Relative Strength Index (RSI).
        Arguments:
        ----
        period {int} -- The number of periods to use to calculate the RSI.
        Keyword Arguments:
        ----
        method {str} -- The calculation methodology. (default: {'wilders'})
        Returns:
        ----
        {pd.DataFrame} -- A Pandas data frame with the RSI indicator included.
        Usage:
        ----
            >>> historical_prices_df = trading_robot.grab_historical_prices(
                start=start_date,
                end=end_date,
                bar_size=1,
                bar_type='minute'
            )
            >>> price_data_frame = pd.DataFrame(data=historical_prices)
            >>> indicator_client = Indicators(price_data_frame=price_data_frame)
            >>> indicator_client.rsi(period=14)
            >>> price_data_frame = inidcator_client.price_data_frame
        """

        locals_data = locals()
        del locals_data['self']

        self._current_indicators[column_name] = {}
        self._current_indicators[column_name]['args'] = locals_data
        self._current_indicators[column_name]['func'] = self.rsi

        # First calculate the Change in Price.
        if 'change_in_price' not in self._frame.columns:
            self.change_in_price()

        # Define the up days.
        self._frame['up_day'] = self._price_groups['change_in_price'].transform(
            lambda x: np.where(x >= 0, x, 0)
        )

        # Define the down days.
        self._frame['down_day'] = self._price_groups['change_in_price'].transform(
            lambda x: np.where(x < 0, x.abs(), 0)
        )

        # Calculate the EWMA for the Up days.
        self._frame['ewma_up'] = self._price_groups['up_day'].transform(
            lambda x: x.ewm(span=period).mean()
        )

        # Calculate the EWMA for the Down days.
        self._frame['ewma_down'] = self._price_groups['down_day'].transform(
            lambda x: x.ewm(span=period).mean()
        )

        # Calculate the Relative Strength
        relative_strength = self._frame['ewma_up'] / self._frame['ewma_down']

        # Calculate the Relative Strength Index
        relative_strength_index = 100.0 - (100.0 / (1.0 + relative_strength))

        # Add the info to the data frame.
        self._frame['rsi'] = np.where(
            relative_strength_index == 0, 100, 100 - (100 / (1 + relative_strength_index)))

        # Clean up before sending back.
        self._frame.drop(
            labels=['ewma_up', 'ewma_down', 'down_day',
                    'up_day', 'change_in_price'],
            axis=1,
            inplace=True
        )

        return self._frame

    def sma(self, period: int, column_name: str = 'sma') -> pd.DataFrame:
        # Calculates the Simple Moving Average (SMA).
        # Arguments:
        # ----
        # period {int} -- The number of periods to use when calculating the SMA.
        # Returns:
        # ----
        # {pd.DataFrame} -- A Pandas data frame with the SMA indicator included.
        # Usage:
        # ----
        #     >>> historical_prices_df = trading_robot.grab_historical_prices(
        #         start=start_date,
        #         end=end_date,
        #         bar_size=1,
        #         bar_type='minute'
        #     )
        #     >>> price_data_frame = pd.DataFrame(data=historical_prices)
        #     >>> indicator_client = Indicators(price_data_frame=price_data_frame)
        #     >>> indicator_client.sma(period=100)

        locals_data = locals()
        del locals_data['self']

        self._current_indicators[column_name] = {}
        self._current_indicators[column_name]['args'] = locals_data
        self._current_indicators[column_name]['func'] = self.sma

        # Add the SMA
        self._frame[column_name] = self._price_groups['close'].transform(
            lambda x: x.rolling(window=period).mean()
        )

        return self._frame

    def ema(self, period: int, alpha: float = 0.0, column_name='ema') -> pd.DataFrame:

        # Calculates the Exponential Moving Average (EMA).
        # Arguments:
        # ----
        # period {int} -- The number of periods to use when calculating the EMA.
        # alpha {float} -- The alpha weight used in the calculation. (default: {0.0})
        # Returns:
        # ----
        # {pd.DataFrame} -- A Pandas data frame with the EMA indicator included.

        locals_data = locals()
        del locals_data['self']

        self._current_indicators[column_name] = {}
        self._current_indicators[column_name]['args'] = locals_data
        self._current_indicators[column_name]['func'] = self.ema

        # Add the EMA
        self._frame[column_name] = self._price_groups['close'].transform(
            lambda x: x.ewm(span=period).mean()
        )

        return self._frame

    def refresh(self):
        """Updates the Indicator columns after adding the new rows."""

        # First update the groups since, we have new rows.
        self._price_groups = self._stock_frame.symbol_groups

        # Grab all the details of the indicators so far.
        for indicator in self._current_indicators:

            # Grab the function.
            indicator_argument = self._current_indicators[indicator]['args']

            # Grab the arguments.
            indicator_function = self._current_indicators[indicator]['func']

            # Update the function.
            indicator_function(**indicator_argument)

    def check_signals(self) -> Union[pd.DataFrame, None]:
        """Checks to see if any signals have been generated.
        Returns:
        ----
        {Union[pd.DataFrame, None]} -- If signals are generated then a pandas.DataFrame
            is returned otherwise nothing is returned.
        """

        signals_df = self._stock_frame._check_signals(
            indicators=self._indicator_signals,
            indciators_comp_key=self._indicators_comp_key,
            indicators_key=self._indicators_key
        )

        return signals_df
