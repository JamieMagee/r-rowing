import os
from configparser import ConfigParser

if os.path.isfile(os.path.join(os.path.dirname(__file__), 'settings.cfg')):
    config = ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'settings.cfg'))

    subreddit = config.get('reddit', 'subreddit')
    username = config.get('reddit', 'username')
    password = config.get('reddit', 'password')

    app_secret = config.get('reddit', 'app_secret')
    access_token = config.get('reddit', 'access_token')
    refresh_token = config.get('reddit', 'refresh_token')
    app_key = config.get('reddit', 'app_key')

    storage_account_name = config.get('azure', 'name')
    storage_account_key = config.get('azure', 'key')
else:
    subreddit = os.getenv('SUBREDDIT')
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')

    app_secret = os.getenv('APP_SECRET')
    access_token = os.getenv('ACCESS_TOKEN')
    refresh_token = os.getenv('REFRESH_TOKEN')
    app_key = os.getenv('APP_KEY')

    storage_account_name = os.getenv('STORAGE_ACCOUNT_NAME')
    storage_account_key = os.getenv('STORAGE_ACCOUNT_KEY')

