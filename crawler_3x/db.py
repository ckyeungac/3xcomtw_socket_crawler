import yaml
import pymongo
from pymongo import MongoClient

with open('./crawler_3x/db_config.yml', 'r') as f:
    config = yaml.load(f)

# Database settings
client = MongoClient(
    config['mongodb']['address'],
    username=config['mongodb']['username'],
    password=config['mongodb']['password'],
    authSource=config['mongodb']['authSource']
)
db = client['trading']

# trade record
tr_collection = db['trade_records']
tr_collection.create_index(
    keys=[("product_code", pymongo.ASCENDING),
          ("datetime", pymongo.DESCENDING)],
    name="_trade_id",
    background=True,
    unique=True
)

# 1min OHLC
ohlc_collection = db['trade_ohlc']
ohlc_collection.create_index(
    keys=[("product_code", pymongo.ASCENDING),
          ("datetime", pymongo.DESCENDING)],
    name="_ohlc_id",
    background=True,
    unique=True
)