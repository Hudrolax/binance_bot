from binance.client import Client
from binance.enums import *
from env import API_KEY, API_SECRET

client = Client(API_KEY, API_SECRET)

# transaction = client.create_margin_loan(asset='USDT', amount=f'{0.01 * 1500}', isIsolated='TRUE', symbol='ETHUSDT')

# order = client.create_margin_order(
#     symbol='ETHUSDT',
#     side=SIDE_BUY,
#     type=ORDER_TYPE_LIMIT,
#     timeInForce=TIME_IN_FORCE_GTC,
#     quantity=0.01,
#     price='1500',
#     isIsolated='TRUE')
# orders = client.get_open_margin_orders(symbol='ETHUSDT', isIsolated='TRUE')
# print(orders)

# result = client.cancel_margin_order(
#     symbol='ETHUSDT',
#     orderId='3145302551',
#     isIsolated='TRUE')
# print(result)

info = client.get_isolated_margin_account()
borrowed = info['assets'][0]['quoteAsset']['borrowed']

transaction = client.repay_margin_loan(asset='USDT', amount=borrowed, isIsolated='TRUE', symbol='ETHUSDT')
print(transaction)