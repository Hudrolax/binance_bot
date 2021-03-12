from time import sleep
from util.base_class import BaseClass
from util.keyboard_input import Keyboard
from binance_bot import BinanceBot
import logging
from datetime import datetime


if __name__ == '__main__':
    WRITE_LOG_TO_FILE = False
    DEBUG_MODE = False

    LOG_FORMAT = '%(name)s (%(levelname)s) %(asctime)s: %(message)s'
    LOG_LEVEL = logging.INFO
    date_format = '%d.%m.%y %H:%M:%S'
    if DEBUG_MODE:
        LOG_LEVEL = logging.DEBUG
    logger = logging.getLogger('main')

    if WRITE_LOG_TO_FILE:
        file_log = logging.FileHandler(f'log_{datetime.now().strftime("%m%d%Y%H%M%S")}.txt', mode='a')
        console_out = logging.StreamHandler()
        logging.basicConfig(handlers=(file_log, console_out), format=LOG_FORMAT, level=LOG_LEVEL,
                            datefmt=date_format)
    else:
        logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL, datefmt=date_format)

    binance_bot = BinanceBot()
    keyboard = Keyboard(binance_bot)

    while BaseClass.working():
        sleep(1)