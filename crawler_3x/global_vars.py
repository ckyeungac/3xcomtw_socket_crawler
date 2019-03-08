from collections import deque

def init():
    global RECENT_TRADE_RECORDS
    global LAST_VOLUME
    global PRICE_DOT
    global PRODUCT_CODE
    RECENT_TRADE_RECORDS = deque(maxlen=5)
    LAST_VOLUME = 0.0
    PRICE_DOT = 0.0
    PRODUCT_CODE = ''