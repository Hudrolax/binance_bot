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
                    if order.trigger_down_price is not None and order.trigger_up and last_price <= order.trigger_down_price:
                        order.trigger_down = True
                        self.logger.info(f'order {order} is triggered down. lets ready to buy at terget price!')

                    if order.price <= last_price < order.price*1.01:
                        if order.trigger_down_price is not None:
                            if not order.trigger_up:
                                order.trigger_up = True
                                self.logger.info(f'order {order} is triggered up!')
                            if not (order.trigger_up and order.trigger_down):
                                return

                        # сначала занимаем деньги
                        if self.get_free_usdt(order.symbol) < order.amount * order.price*1.004:
                            self.create_usdt_loan(order.symbol, order.amount * order.price*1.004 - self.get_free_usdt(order.symbol))
                        # открываем ордер
                        created_order = self.create_order(order.symbol, order.side, order.amount, order.price*1.003, order.market)
                        self.meta_orders.remove(order)
                        self.logger.info(f'remove planned order: {order}')
                elif order.side == 'SELL':
                    if order.price >= last_price > order.price * 1.007:
                        # открываем ордер
                        created_order = self.create_order(order.symbol, order.side, order.amount, order.price*0.997, order.market)
                        if created_order is not None:
                            # возвращаем заем
                            self.repay_usdt_loan(order.symbol, self.get_borrowed(order.symbol))


    def _get_margin_info(self):
        self.margin_info = self.client.get_isolated_margin_account()

    def _get_prices(self):
        self.prices = self.client.get_all_tickers()

    def create_usdt_loan(self, symbol, amount):
        try:
            transaction = self.client.create_margin_loan(asset='USDT', amount=str(round(amount,2)), isIsolated='TRUE', symbol=symbol)
            self.logger.info(transaction)
        except Exception as ex:
            self.logger.error(f'borrow error: {ex}')

    def repay_usdt_loan(self, symbol, amount):
        try:
            transaction = self.client.repay_margin_loan(asset='USDT', amount=str(round(amount,2)), isIsolated='TRUE', symbol=symbol)
            self.logger.info(transaction)
        except Exception as ex:
            self.logger.error(f'repay error: {ex}')

    def create_order(self, symbol, side, amount, price, market='spot'):
        try:
            if market == 'margin':
                order = self.client.create_margin_order(
                    symbol=symbol.upper(),
                    side=side.upper(),
                    type='LIMIT',
                    quantity=amount,
                    timeInForce='GTC',
                    price=str(price),
                    isIsolated='TRUE')
            else:
                order = self.client.create_order(
                    symbol=symbol.upper(),
                    side=side.upper(),
                    type='LIMIT',
                    price=str(price),
                    quantity=amount)
            self.logger.info(order)
            return order
        except Exception as ex:
            self.logger.error(f'open order error: {ex}')

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

    def get_free_usdt(self, symbol, asset_param = 'quoteAsset'):
        if isinstance(self.margin_info, dict) and isinstance(symbol, str):
            assets = self.margin_info['assets']
            for asset in assets:
                if asset['symbol'] == symbol.upper():
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
                return
            symbol = cmd_list[1]
            amount = cmd_list[2]
            self.create_usdt_loan(symbol, amount)
        elif cmd_list[0] == 'delete':
            self.meta_orders = []
            print('all orders deleted')
        elif cmd_list[0] == 'repay':
            if len(cmd_list) != 2:
                print('wrong format. ex.: repay btcusdt')
                return
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
                    return
        else:
            meta_order = MetaOrder(cmd_list = cmd_list)
            if meta_order.inited:
                self.meta_orders.append(meta_order)
                print(f'add order: {meta_order}')