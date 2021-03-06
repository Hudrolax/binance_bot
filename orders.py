class MetaOrder:
    def __init__(self, **params):
        self.inited = False
        self.market = params.get('market')
        self.symbol = params.get('symbol')
        self.side = params.get('side')
        self.price = params.get('price')
        self.amount = params.get('amount')
        self.trigger_down_price = params.get('trigger_down_price')
        self.trigger_up = False
        self.trigger_down = False
        self.TP = params.get('TP')

        cmd_list = params.get('cmd_list')
        for cmd in enumerate(cmd_list):
            if cmd[0] == 0:
                self.market = str(cmd[1]).lower()
                if self.market != 'spot' and self.market != 'margin':
                    print('wrong market format. Need spot or margin')
                    return
            if cmd[0] == 1:
                self.side = str(cmd[1]).upper()
                if self.side != 'SELL' and self.side != 'BUY':
                    print('wrong side format. Need sell or buy')
                    return
            elif cmd[0] == 2:
                self.symbol = str(cmd[1]).upper()
            elif cmd[0] == 3:
                try:
                    self.amount = float(cmd[1])
                except:
                    print('wrong amount format')
                    return
            elif cmd[0] == 4:
                try:
                    self.price = float(cmd[1])
                except:
                    print('wrong price format')
                    return
            elif cmd[0] == 5:
                try:
                    if cmd[1] != 'None':
                        self.trigger_down_price = float(cmd[1])
                    else:
                        self.trigger_down_price = None
                except:
                    print('wrong trigger_down_price format')
                    return
            elif cmd[0] == 6:
                try:
                    if cmd[1] != 'None':
                        self.TP = float(cmd[1])
                    else:
                        self.TP = None
                except:
                    print('wrong TP format')
                    return
        self.inited = True

    def __str__(self):
        return f'{self.market} {self.side} {self.symbol} amount {self.amount} price {self.price} trigger down price {self.trigger_down_price} TP {self.TP}'