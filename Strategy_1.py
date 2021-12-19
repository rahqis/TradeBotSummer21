import json
import pprint
from re import T
import pandas as pd
import operator
import time as true_time
from datetime import datetime as dt
from datetime import timedelta
from configparser import ConfigParser

from td.client import TDClient
from Bot.trade import Trade
from Bot.robot_frame import robotFrame
from Bot.indicator import Indicators

# Read config
config = ConfigParser()
config.read('Configurations/config.ini')

# Read different values
CLIENT_ID = config.get("main", "CLIENT_ID")
REDIRECT_URI = config.get("main", "REDIRECT_URI")
ACCOUNT_NUMBER = config.get("main", "CLIENT_ID")
JSON_PATH = config.get("main", "JSON_PATH")


# Initialize the Robot Frame Object
trading_bot = robotFrame(
    client_id=CLIENT_ID,
    redirect_uri=REDIRECT_URI,
    creds=JSON_PATH,
    acct=ACCOUNT_NUMBER,
    paper_trading=True
)

# Initialize Portfolio
trading_bot.new_portfolio()
bot_portfolio = trading_bot.portfolio

# Define Trading Symbol
trading_symbol = 'FCEL'

# Add Single Position
bot_portfolio.add_position(
    symbol=trading_symbol,
    asset_type='equity',

)

# Grab Historical Data
start_date = dt.today()
end_date = start_date-timedelta(days=30)

historical_prices = trading_bot.hist_quote(
    start=end_date,
    end=start_date,
    bar_size=1,
    bar_type='minute'
)

# Convert data to stock frame
stock_frame = trading_bot.new_stock_frame(
    data=historical_prices['aggregated']
)

# Add stock frame to portfolio
trading_bot.portfolio.stock_frame = stock_frame
trading_bot.portfolio._historical_prices = historical_prices

# Create new Indicator Object
indicator_client = Indicators(price_data_frame=stock_frame)

# Add 200-day SMA
indicator_client.sma(period=200, column_name='sma_200')

# Add 50-day SMA
indicator_client.sma(period=50, column_name='sma_50')

# Add 50-day EMA
indicator_client.ema(period=50, column_name='ema_50')

# Add Signal Check
indicator_client.set_indicator_signal_compare(
    indicator_1='sma_50',
    indicator_2='sma_200',
    condition_buy=operator.ge,
    condition_sell=operator.le
)

# Create new Trade Object entering position
new_long_trade = trading_bot.create_trade(
    trade_id='long_enter',
    enter_or_exit='enter',
    long_or_short='long',
    order_type='mkt'
)

# Add an Order leg
new_long_trade.instrument(
    symbol=trading_symbol,
    quantity=1,
    asset_type='EQUITY'
)

# Create new Trade Object exiting position
new_exit_trade = trading_bot.create_trade(
    trade_id='long_exit',
    enter_or_exit='exit',
    long_or_short='long',
    order_type='mkt'
)

# Add an Order leg
new_exit_trade.instrument(
    symbol=trading_symbol,
    quantity=1,
    asset_type='EQUITY'
)


def default(obj):
    if isinstance(obj, TDClient):
        return str(TDClient)


# Save orders
with open(file='order_strategies.jsonc', mode='w+') as order_file:
    json.dump(
        new_long_trade.to_dict(), new_exit_trade.to_dict(),
        fp=order_file,
        default=default,
        indent=4
    )

# Define trading Dictionary
trades_dict = {
    trading_symbol: {
        'buy': {
            'trade_funct': trading_bot.trades['long_enter'],
            'trade_id': trading_bot.trades['long_enter'].trade_id
        },
        'sell': {
            'trade_funct': trading_bot.trades['long_exit'],
            'trade_id': trading_bot.trades['long_exit'].trade_id
        }
    }
}

# Define ownership status
ownership_dict = {
    trading_symbol: False
}

# Intialize Order Variable
order = None

while trading_bot.is_reg_open:

    # Grab latest bar
    latest_bar = trading_bot.get_latest_bar()

    # Add latest bar to stock frame
    stock_frame.add_rows(data=latest_bar)

    # Refresh indicators
    indicator_client.refresh()
    print("-"*50)
    print("Current Stock Stock: ")
    print("-"*50)
    print(stock_frame.symbol_groups.tail())
    print("-"*50)
    print("")

    # Check for signals
    signals = indicator_client.check_signals()

    # Define the buy and sell signals
    buys = signals['buy'].to_list()
    sells = signals['sell'].to_list()

    print("-"*50)
    print("Current Signals: ")
    print("-"*50)
    print("Symbols: {}".format(list(trades_dict.keys())[0]))
    print("Ownership Status: {}".format(ownership_dict[trading_symbol]))
    print("Buy: {}".format(buys))
    print("Sells: {}".format(sells))
    print("-"*50)
    print("")

    if ownership_dict[trading_symbol] is False and buys:

        # Execute Trade
        trading_bot.execute_signals(
            signals=signals,
            trades_to_execute=trades_dict
        )

        ownership_dict[trading_symbol] = True
        buy_order: Trade = trades_dict[trading_symbol]['buy']['trade_funct']

    elif ownership_dict[trading_symbol] is True and sells:

        # Execute Trade
        trading_bot.execute_signals(
            signals=signals,
            trades_to_execute=trades_dict
        )

        ownership_dict[trading_symbol] = False
        buy_order: Trade = trades_dict[trading_symbol]['sell']['trade_funct']

    # Grab last row
    last_row = trading_bot.stock_frame.frame.tail(n=1)

    # Grab last timestamp
    last_bar_timestamp = last_row.index.get_level_values(1)

    # Wait till next bar
    trading_bot.wait_till_next_bar(last_bar_timestap=last_bar_timestamp)

    # if order:
    #     order.check_status()
