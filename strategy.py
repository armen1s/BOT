import pandas as pd
from sl import SL
from talib import RSI

class Strategy:
    def __init__(self, exchange, symbol, leverage, position_size, frame):
        self.exchange = exchange
        self.symbol = symbol
        self.leverage = leverage
        self.position_size = position_size
        self.frame = frame
        self.sl = SL(is_dinamic=True, coef=0.25)

    def get_rsi(self, kline):
        close_prices = [x[4] for x in kline]
        rsi = RSI(close_prices, timeperiod=2)
        return rsi[-1]

    def get_trade_type(self, kline):
        rsi = self.get_rsi(kline)
        if rsi > 35:
            return 1  # покупка
        elif rsi < 55:
            return -1  # продажа
        else:
            return None

    def get_position_size(self):
        return self.position_size

    def get_stop_loss(self, kline, trade_type):
        return self.sl.get_sl(pd.DataFrame(kline, columns=['open', 'high', 'low', 'close', 'volume']), trade_type)
