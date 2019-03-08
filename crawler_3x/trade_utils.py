import datetime
import time
import uuid
from pymongo.errors import DuplicateKeyError
from crawler_3x import global_vars
from crawler_3x.constants import product_timezone, product_name
from crawler_3x.db import tr_collection
from crawler_3x.logger import logger

def json_serial(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    if isinstance(obj, uuid.UUID):
        return obj.hex

def get_trade_datetime(t):
    """
    Receive time in format 'HH:MM:SS'. Convert it to a datetime object.
    Arguments:
      - t: str
    
    Return:
      - trade_datetime: datetime object with timezone information
    """
    product_code = global_vars.PRODUCT_CODE

    trade_time = t.split(':')  # HH:MM:SS
    trade_hour = int(trade_time[0])
    trade_minute = int(trade_time[1])
    trade_second = int(trade_time[2])
    trade_datetime = datetime.datetime.now(product_timezone[product_code])

    # avoid edge cases
    _hour = trade_datetime.hour
    if _hour == 0 and trade_hour == 23:
        trade_datetime = trade_datetime.replace(
            hour=trade_hour, minute=trade_minute, second=trade_second, microsecond=1000
        )
        trade_datetime = trade_datetime - datetime.timedelta(days=1)
    else:
        trade_datetime = trade_datetime.replace(
            hour=trade_hour, minute=trade_minute, second=trade_second, microsecond=1000
        )

    # keep the ordering
    recent_trade_records = global_vars.RECENT_TRADE_RECORDS
    if len(recent_trade_records) != 0:
        last_trade_datetime = recent_trade_records[-1]['datetime']
        _last_trade_datetime = last_trade_datetime.replace(microsecond=0)
        _trade_datetime = trade_datetime.replace(microsecond=0)
        if _trade_datetime == _last_trade_datetime:
            trade_datetime = trade_datetime.replace(
                microsecond=last_trade_datetime.microsecond + 1000
            )
    
    return trade_datetime


# TODO: add custom measurments
def process_trade_data(trade_data):
    """
    Parameters:
        - trade_data: str
            e.g., 'O1GCJ|11:31:44|13046|13044|13046|220834|'
    """
    assert isinstance(trade_data, str), "String is expected"
    assert len(trade_data.split('|')) == 7, \
            "Format of '<prod_id>|<trade_time>|<ask_price>|<bid_price>|<exercise_price>|<total_volume>|' is expected."
    
    # read global variables
    price_dot = global_vars.PRICE_DOT
    last_volume = global_vars.LAST_VOLUME
    recent_trade_records = global_vars.RECENT_TRADE_RECORDS
    product_code = global_vars.PRODUCT_CODE
    
    # initialization
    data = trade_data.split('|')
    trade_record = dict()
    trade_record['uuid'] = uuid.uuid4()

    # trade info
    trade_record['product_id'] = data[0]
    trade_record['product_code'] = product_code
    trade_record['product_name'] = product_name[product_code]
    trade_record['datetime'] = get_trade_datetime(data[1])
    trade_record['datetime_str'] = trade_record['datetime'].isoformat()

    # trade detail
    trade_record['ask_price'] = int(data[2]) / 10.**price_dot
    trade_record['bid_price'] = int(data[3]) / 10.**price_dot
    trade_record['exercise_price'] = int(data[4]) / 10.**price_dot

    # total volume upto this trade
    curr_volume = int(data[5])
    trade_record['volume'] = curr_volume

    # amount of this trade
    if len(recent_trade_records) != 0:
        # if race condition occurs with the data from 'GD', use the last record
        if curr_volume == last_volume:
            last_volume = RECENT_TRADE_RECORDS[-1]['volume']
        # if (current time > last time) but (current volume < last volume)
        elif trade_record['datetime'] > recent_trade_records[-1]['datetime']\
            and curr_volume < last_volume:
            # assume it happens only when it starts a new trade history
            # so set the last_volume to 0
            last_volume = 0.0
    trade_record['amount'] = curr_volume - last_volume
    last_volume = curr_volume

    # update the global last_volume
    global_vars.LAST_VOLUME = last_volume

    return trade_record

def save_trade_data(trade_data):
    start_time = time.time()
    trade_record = process_trade_data(trade_data)

    # save to database
    try:
        # the unique index is (product_code, datetime)
        trade_record_id = tr_collection.insert_one(trade_record).inserted_id
        logger.debug("Trade ({}, {}), Inserted to mongoDB with _id {}. (Time used: {:.3}ms)".format(
            trade_record['product_code'], trade_record['datetime_str'], 
            trade_record_id, (time.time() - start_time) * 1000)
        )
    except DuplicateKeyError:
        logger.debug("Trade ({}, {}) already exists in the database.").format(
            trade_record['product_code'], trade_record['datetime_str']
        )

    # append to the deque
    global_vars.RECENT_TRADE_RECORDS.append(trade_record)