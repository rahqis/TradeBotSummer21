# Last Updated: Rahqi Sarsour 4:20 PM 06/17/21
import time as true_time
import pprint
import pathlib
import operator
import pandas as pd

from datetime import datetime as dt
from datetime import timedelta as delta
from configparser import ConfigParser

from Bot.robot_frame import robotFrame
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
pprint.pprint(current_quotes)
