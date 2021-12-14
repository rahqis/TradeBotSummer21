# Last Updated: Rahqi Sarsour 4:20 PM 06/17/21
import time as true_time
import pprint
import pathlib
import operator
import pandas as pd

from datetime import datetime as dt, timedelta
from datetime import timedelta as delta
from configparser import ConfigParser
from Bot.indicator import Indicators

from Bot.robot_frame import robotFrame
from Bot.stock_frame import StockFrame
# from Bot.indicator import Indicators

config = ConfigParser()
config.read('configurations/config.ini')

CLIENT_ID = config.get('main', 'CLIENT_ID')
REDIRECT_URI = config.get('main', 'REDIRECT_URI')
CREDS_PATH = config.get('main', 'JSON_PATH')
ACCT_NUM = config.get('main', 'ACCOUNT_NUMBER')

# Initializes Bob
trading_bot = robotFrame(
    client_id=CLIENT_ID,
    redirect_uri=REDIRECT_URI,
    creds=CREDS_PATH,
    acct=ACCT_NUM
    # Can explicitly declare paper_trading, but it defaults to true if no params exist for it
)

# New Portfolio
trading_bot_portfolio = trading_bot.new_portfolio()

# Test to add multiple positions
multi_position = [
    {
        'assert_type': 'equity',
        'quantity': 2,
        'price': 4.00,
        'ticker': 'TSLA',
        'purchase_date': '2021-01-31'
    },
    {
        'assert_type': 'equity',
        'quantity': 2,
        'price': 4.00,
        'ticker': 'MSFT',
        'purchase_date': '2021-01-31'
    }
]

new_positions = trading_bot.portfolio.new_position_collection(
    positions=multi_position
)
pprint.pprint(new_positions)

# Test to add single position
trading_bot.portfolio.new_position(
    ticker='TSLA',
    quantity=12,
    price=15.99,
    asset_type='equity',
    purchase_date='2020-04-01'
)
pprint.pprint(trading_bot.portfolio.positions)

# Test to check is market is open
if trading_bot.is_reg_open:
    print('Market is Open')
else:
    print('Market is Open')

if trading_bot.is_pre_market:
    print('Pre-Market is Open')
else:
    print('Pre-Market is Open')

if trading_bot.is_after_hours:
    print('After Hours are Open')
else:
    print('After Hours are Open')

# Grabbing current quotes for portfolio
current_quotes = trading_bot.updated_quote()
# pprint.pprint(current_quotes)


# define date range
end_date = dt.today()
start_date = end_date - timedelta(days=30)

# hist prices

hist_prices = trading_bot.hist_quote(
    start=start_date,
    end=end_date,
    bar_size=1,
    bar_type='minute',
)

# convert data to stock frame

stock_frame = trading_bot.new_stock_frame(data=hist_prices['aggregated'])

# print head of stock frame

pprint.pprint(stock_frame.frame.head(n=20))

# init new trade obj
new_trade = trading_bot.create_trade(
    trade_id='long_msft',
    enter_or_exit='exit',
    long_or_short='long',
    order_type='lmt',
    price=150.00,
)

# Good til cancel
new_trade.good_till_cancel(cancel_time=dt.utcnow() + timedelta(minutes=90))

# mod session


# add order leg
new_trade.get_instrument(
    ticker='MSFT',
    quantity=2,
    asset_type='EQUITY'
)

# add stop loss

pprint.pprint(new_trade.order)


# Create new indicator client

indicator_client = Indicators(price_data_frame=stock_frame)

# Add rsi
indicator_client.rsi(period=14)

# Add sma of 200 days
indicator_client.sma(period=200)

# Add 50 day exponential moving average
indicator_client.ema(period=50)

# Add signal to check for
indicator_client.set_indicator_signal(
    indicator='rsi',
    buy=40.0,
    sell=20.0,
    condition_buy=operator.ge,
    condition_sell=operator.le
)

trade_dict = {
    'MSFT': {
        'trade_func': trading_bot.trades['long_msft'],
        'trade_id': trading_bot.trades['long_msft'].trade_id
    }
}

while True:

    # Grab latest bot
    latest_bar = trading_bot.get_latest_bar()

    # Add bars to stock fram
    stock_frame.add_rows(data=latest_bar)

    # Refresh indicts
    indicator_client.refresh()

    print("="*50)
    print("Current Stock Frame")
    print("-"*50)
    print(stock_frame.symbol_groups.tail())
    print("-"*50)
    print("")

    # Check signals
    signals = indicator_client.check_signals()

    # Exec Trades
    trading_bot.execute_signals(signals=signals, trades_to_execute=trade_dict)

    # Grab last bar after adding new rows
    last_bar_ts = trading_bot.stock_frame.frame.tail(
        1).index.get_level_values(1)

    # Wait til next bar
    trading_bot.wait_till_next_bar(last_bar_timestap=last_bar_ts)
