import argparse
import json
import time
import datetime
import websocket
from collections import deque
from crawler_3x import global_vars
from crawler_3x.constants import product_timezone
from crawler_3x.logger import logger
from crawler_3x.trade_utils import process_tick


###############################################
#                   Websocket                 #
###############################################
def on_open(ws):
    """
    start listening to the websocket
    """
    # send request to start listening
    start_up_msg1 = '{"t":"GL","p":"%s"}' % global_vars.PRODUCT_CODE
    start_up_msg2 = '{"t":"GPV"}'
    ws.send(start_up_msg1)
    ws.send(start_up_msg2)
    logger.info("[{}] (on_open) ws.send({})".format(global_vars.PRODUCT_CODE, start_up_msg1))
    logger.info("[{}] (on_open) ws.send({})".format(global_vars.PRODUCT_CODE, start_up_msg2))

def on_close(ws):
    """
    close the websocket
    """
    logger.info("[{}] ### closed ###".format(global_vars.PRODUCT_CODE))
    
def on_message(ws, message):
    """
    The message that is of important is of type "GN". Here is an example:
    {'d': 'O1GCJ|11:31:44|13046|13044|13046|220834|', 't': 'GN'}
    
    This can be interpreted as
    {
        'd': '<prod_id>|<trade_time>|<ask_price>|<bid_price>|<exercise_price>|<total_volume>|', 
        't': 'GN'
    }
    """
    logger.debug(message[:256])
    message = json.loads(message)
    
    # message type of "Get Now"
    if message.get('t') == 'GN':
        d = message.get('d')
        if d is not None and len(d.split('|')) == 7:
            process_tick(d)

    # type of "Get Last"
    elif message.get('t') == 'GL':
        global_vars.PRICE_DOT = float(message.get('pd', 0.0))

    # type of "Get Daily"
    elif message.get('t') == 'GD':
        d = message.get('d')
        if d is not None and len(d.split('|')) == 9:
            # update the updated volume in case the program miss some records
            data = d.split('|')
            _last_volume = int(data[2])
            if _last_volume > global_vars.LAST_VOLUME:
                global_vars.LAST_VOLUME = _last_volume
    
    # type of "Get Pic200"
    elif message.get('t') == 'GP':
        global_vars.PRICE_DOT = float(message.get('pd', 0.0))
        d = message.get('d')
        recent_trade_data = d.split(', ')
        for trade_data in recent_trade_data:
            if len(trade_data.split('|')) == 7:
                process_tick(trade_data)

def on_error(ws, error):
    logger.error("[{}] error: {}".format(global_vars.PRODUCT_CODE, error))

if __name__ == "__main__":
    # argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--product", type=str, default="O1GC")
    args = parser.parse_args()

    # initialize the global variables
    global_vars.init()
    global_vars.PRODUCT_CODE = args.product    
    global_vars.RECENT_TRADE_RECORDS = deque(maxlen=5)
    global_vars.LAST_VOLUME = 0.0
    global_vars.PRICE_DOT = 0.0

    # initialize websocket
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        "ws://m.3x.com.tw:5490",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    # run the websocket
    ws.run_forever()
