import argparse
import datetime
import json
import logging
from multiprocessing import Process, Manager
from pymongo import MongoClient
import pytz
import time
import websocket
import yaml
import uuid

###############################################
#                 Configuration               #
###############################################
with open('config.yml', 'r') as f:
    config = yaml.load(f)

###############################################
#                   Argparser                 #
###############################################
parser = argparse.ArgumentParser()
parser.add_argument("--product", type=str, default="O1GC")
args = parser.parse_args()

# create logger with 'spam_application'
logger = logging.getLogger('3xdotcom_websocket_crawler')
logger.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s -  %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

###############################################
#                 Multithreading              #
###############################################
# Shared memory between process
manager = Manager()
shared_dict = manager.dict()
shared_dict['last_check_time'] = time.time()

# Process 
checker_process = None

###############################################
#                    Database                 #
###############################################
# Database settings
client = MongoClient(
    config['mongodb']['address'],
    username=config['mongodb']['username'],
    password=config['mongodb']['password'],
    authSource=config['mongodb']['authSource']
)
db = client['trading']
tr_collection = db['trade_records']

###############################################
#                  data dict                  #
###############################################
product_timezone = {
    'HSI': pytz.timezone('Asia/Hong_Kong'),  # Heng Seng
    'HSCE': pytz.timezone('Asia/Hong_Kong'),  # 
    'IF300': pytz.timezone('Asia/Hong_Kong'),  # Shanghai and Shenzhen index
    'S2SFC': pytz.timezone('Asia/Hong_Kong'),  # A50
    'O1GC': pytz.timezone('America/New_York'),  # Gold
    'M1EC': pytz.timezone('America/Chicago'),  # Euro
    'B1YM': pytz.timezone('America/Chicago'),  # Mini Dow Jones
    'N1CL': pytz.timezone('America/New_York'),  # Oil
    'WTX': pytz.timezone('Asia/Taipei'),  # Taiwan
    'M1NQ': pytz.timezone('America/Chicago'),  # NasDaq
    'M1ES': pytz.timezone('America/Chicago'),  # SP500
}

product_name = {
    'HSI': "亞洲期指",  # Heng Seng
    'HSCE': "亞企期指",  # 
    'IF300': "滬深期指",  # Shanghai and Shenzhen index
    'S2SFC': "A50",  # A50
    'O1GC': "紐約期金",  # Gold
    'M1EC': "歐元期貨",  # Euro
    'B1YM': "迷你道瓊",  # Mini Dow Jones
    'N1CL': "小輕原油",  # Oil
    'WTX': "台灣期指",  # Taiwan
    'M1NQ': "NasDaq",  # NasDaq
    'M1ES': "SP500",  # SP500
}

###############################################
#                   Websocket                 #
###############################################
# Listening to websocket
price_dot = 0.0
last_volume = 0
product = args.product

def json_serial(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    if isinstance(obj, uuid.UUID):
        return obj.hex

def get_trade_datetime(t):
    global product
    global product_timezone

    trade_time = t.split(':')  # HH:MM:SS
    trade_hour = int(trade_time[0])
    trade_minute = int(trade_time[1])
    trade_second = int(trade_time[2])
    
    trade_datetime = datetime.datetime.now(product_timezone[product])
    trade_datetime = trade_datetime.replace(
        hour=trade_hour, minute=trade_minute, second=trade_second
    )
    
    return trade_datetime

# send ws query every 30 seconds
def check(ws):
    while True:
        now = int(time.time())
    
        start_up_msg1 = '{"t":"GL","p":"%s"}' % product
        start_up_msg2 = '{"t":"GPV"}'
        ws.send(start_up_msg1)
        ws.send(start_up_msg2)
        logger.info("ws.send({})".format(start_up_msg1))
        logger.info("ws.send({})".format(start_up_msg2))

        shared_dict['last_check_time'] = now
        time.sleep(30)

def on_open(ws):
    """
    When we send 
        - {"t":"GL","p":"<$code>"}, and
        - {"t": "GPV"}
    to the websocket of m.3x.com.tw:5490, we will get each trade data of the <$code>
    
    <$code> can be
        - "HSI" - 亞洲期指 (depecated)
        - "HSCE" - 亞企期指 (depecated)
        - "IF300" - 滬深期指
        - "S2SFC" - A50
        - "O1GC" - 紐約期金
        - "M1EC" - 歐元期貨
        - "B1YM" - 迷你道瓊
        - "N1CL" - 小輕原油
        - "WTX" - 台灣期指
        - "M1NQ" - NasDaq
        - "M1ES" - SP500
    """

    # Checker Process
    global checker_process
    checker_process = Process(target=check, args=(ws,))
    checker_process.start()

def on_close(ws):
    global checker_process
    if checker_process:
        checker_process.join(3)  # wait for this process to complete for 3 seconds
    logger.info("### closed ###")

def on_error(ws, error):
    logger.error(error)
    
def on_message(ws, message):
    """
    The message are of important is of "GN". Here is an example:
    {'d': 'O1GCJ|11:31:44|13046|13044|13046|220834|', 't': 'GN'}
    
    This can be interpreted as
    {'d': '<prod_id>|<prod_time_info>|<ask_price>|<bid_price>|<exercise_price>|<total_volume>|', 't': 'GN'}
    """
    global price_dot
    global last_volume
    
    message = json.loads(message)
    logger.info(message)
    
    if message.get('t') == 'GN':
        d = message.get('d')
        if d is not None and len(d.split('|')) == 7:
            start_time = time.time()
            data = d.split('|')
        
            trade_record = dict()
            trade_record['uuid'] = uuid.uuid4()
            trade_record['product_id'] = data[0]
            trade_record['product_name'] = product_name[product]
            trade_record['datetime'] = get_trade_datetime(data[1])
            trade_record['datetime_str'] = trade_record['datetime'].isoformat()
            trade_record['ask_price'] = int(data[2]) / 10.**price_dot
            trade_record['bid_price'] = int(data[3]) / 10.**price_dot
            trade_record['exercise_price'] = int(data[4]) / 10.**price_dot
            curr_volume = int(data[5])
            trade_record['volume'] = curr_volume
            trade_record['amount'] = curr_volume - last_volume
            last_volume = curr_volume
            
            # save to database
            trade_record_id = tr_collection.insert_one(trade_record).inserted_id
            logger.info("{}, Inserted to mongoDB with id {}. (Time used: {:.3}ms)".format(
                trade_record, trade_record_id, (time.time() - start_time) * 1000)
            )

    elif message.get('t') == 'GL':
        price_dot = float(message.get('pd', 0.0))
    elif message.get('t') == 'GD':
        d = message.get('d')
        if d is not None and len(d.split('|')) == 9:
            data = d.split('|')

            # update the updated volume
            _last_volume = int(data[2])
            if _last_volume > last_volume:
                last_volume = _last_volume


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        "ws://m.3x.com.tw:5490",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
    )
    ws.run_forever()


