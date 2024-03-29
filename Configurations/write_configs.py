# Last Updated: Rahqi Sarsour 8:09 PM 06/17/21

from configparser import ConfigParser

config = ConfigParser()

config.add_section('main')
config.set('main', 'CLIENT_ID', '')
config.set('main', 'REDIRECT_URI', '')
config.set('main', 'JSON_PATH', '')
config.set('main', 'ACCOUNT_NUMBER', '')

with open('configurations/config.ini', 'w+') as f:
    config.write(f)
