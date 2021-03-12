from binance.client import Client
from binance.enums import ORDER_STATUS_NEW, ORDER_STATUS_FILLED, ORDER_STATUS_CANCELED, ORDER_TYPE_STOP_LOSS
from env import API_KEY, API_SECRET
from orders import MetaOrder
from util.base_class import BaseClass
from util.logger_super import LoggerSuper
import threading
import logging
from time import sleep

class BinanceBot(LoggerSuper):
    logger = logging.getLogger('BinanceBot')
    def __init__(self):
        self.client = Client(API_KEY, API_SECRET)
        self.meta_orders = []
        self.prices = None
        self.margin_info = None

        self.botThread = threading.Thread(target=self.botThreadfunc, args=(), daemon=False)
        self.botThread.start()
        self.logger.info('bot started')
        print('add order: {margin/spot} {side} {symbol} {amount} {price} {TP} {SL}')
        print('symbol info: {symbol}')
        print('borrow USDT: borrow {symbol} {amount}')
        print('repay USDT: repay {symbol}')

    def botThreadfunc(self):
        while BaseClass.working():
            self._transaction(self._get_prices)
            self._transaction(self._get_margin_info)
            self.check_and_place_orders()

            sleep(1)

    def _transaction(self, foo):
        try:
            foo()
        except Exception as Ex:
            self.logger.error(Ex)

    def check_and_place_orders(self):
        for order in self.meta_orders:
            if order.id is None:
                created_order = None
                last_price = self.get_price(order.symbol)
                if order.side == 'BUY':
                    if order.price <= last_price < order.price*1.007:
                        created_order = self.create_order(order.symbol, order.side, order.amount, order.market)
                elif order.side == 'SELL':
                    pass
                if created_order is not None:
                    self.meta_orders.remove(order)
                    self.logger.info(f'remove planned order: {order}')

    def _get_margin_info(self):
        self.margin_info = self.client.get_isolated_margin_account()

    def _get_prices(self):
        self.prices = self.client.get_all_tickers()

    def create_usdt_loan(self, symbol, amount):
        transaction = self.client.create_margin_loan(asset='USDT', amount=str(amount), isIsolated='TRUE', symbol=symbol)
        self.logger.info(transaction)

    def repay_usdt_loan(self, symbol, amount):
        transaction = self.client.repay_margin_loan(asset='USDT', amount=str(amount), isIsolated='TRUE', symbol=symbol)
        self.logger.info(transaction)

    def create_order(self, symbol, side, amount, market='spot'):
        try:
            if market == 'margin':
                order = self.client.create_margin_order(
                    symbol=symbol.upper(),
                    side=side.upper(),
                    type='MARKET',
                    timeInForce='GTC',
                    quantity=amount,
                     isIsolated='TRUE')
            else:
                order = self.client.create_order(
                    symbol=symbol.upper(),
                    side=side.upper(),
                    type='MARKET',
                    quantity=amount)
            self.logger.info(order)
            return order
        except Exception as ex:
            self.logger.error(ex)

    def orders(self):
        if len(self.meta_orders) > 0:
            for meta_order in self.meta_orders:
                print(meta_order)
        else:
            print('No meta orders')

    def get_price(self, pair):
        if isinstance(self.prices, list) and isinstance(pair, str):
            for price in self.prices:
                if price['symbol'] == pair.upper():
                    return float(price['price'])
        else:
            return None

    def get_borrowed(self, pair, asset_param = 'quoteAsset'):
        if isinstance(self.margin_info, dict) and isinstance(pair, str):
            assets = self.margin_info['assets']
            for asset in assets:
                if asset['symbol'] == pair.upper():
                    return float(asset[asset_param]['borrowed']) + float(asset[asset_param]['interest'])
        else:
            return None

    def get_free_usdt(self, pair, asset_param = 'quoteAsset'):
        if isinstance(self.margin_info, dict) and isinstance(pair, str):
            assets = self.margin_info['assets']
            for asset in assets:
                if asset['symbol'] == pair.upper():
                    return float(asset[asset_param]['free'])
        else:
            return None

    def keyboard_notify(self, owner):
        cmd_list = owner.get()
        if len(cmd_list) == 0:
            return
        if cmd_list[0] == 'borrow':
            if len(cmd_list) != 3:
                print('wrong format. ex.: borrow btcusdt 30000')
            symbol = cmd_list[1]
            amount = cmd_list[2]
            self.create_usdt_loan(symbol, amount)
        if cmd_list[0] == 'repay':
            if len(cmd_list) != 2:
                print('wrong format. ex.: repay btcusdt')
            symbol = cmd_list[1]
            self.repay_usdt_loan(symbol, self.get_borrowed(symbol))
        elif len(cmd_list) == 1:
            if cmd_list[0] == 'orders':
                self.orders()
            else:
                symbol = cmd_list[0]
                price = self.get_price(symbol)
                borrowed = self.get_borrowed(symbol)
                if price is not None:
                    print(f'{symbol}: price {price}. Borrowed {borrowed} USDT.')
                else:
                    print('wrong pair')
        else:
            meta_order = MetaOrder(cmd_list = cmd_list)
            if meta_order.inited:
                self.meta_orders.append(meta_order)
                print(f'add order: {meta_order}')