import logging
import datetime

# create logger
logger = logging.getLogger('3xdotcom_crawler')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s -  %(message)s')
# create file handler which logs even debug messages
fh = logging.FileHandler('./logs/crawler_3x-{}.log'.format(datetime.datetime.now().date()))
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)