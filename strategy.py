# strategy.py

import pandas as pd
from sl import SL
from talib import RSI

class Strategy:
    def init(self, exchange, symbol, leverage, position_size, frame, take_profit_coef):
        self.exchange = exchange
        self.symbol = symbol
        self.leverage = leverage
        self.position_size = position_size
        self.frame = frame
        self.sl = SL(is_dynamic=True, coef=0.25)
        self.take_profit_coef = take_profit_coef

    def get_rsi(self, kline):
        close_prices = [x[4] for x in kline]
        rsi = RSI(close_prices, timeperiod=2)
        return rsi[-1]

    def get_trade_type(self, kline):
        rsi = self.get_rsi(kline)
        if rsi < 35:
            return 'buy'  # покупка
        elif rsi > 55:
            return 'sell'  # продажа
        else:
            return None

    def get_position_size(self):
        return self.position_size

    def get_stop_loss(self, kline, trade_type):
        return self.sl.get_sl(pd.DataFrame(kline, columns=['open', 'high', 'low', 'close', 'volume']), trade_type)

    def get_take_profit(self, kline, trade_type):
        price = kline[-1][4]  # последняя цена закрытия
        if trade_type == 'buy':
            return price + price * self.take_profit_coef
        elif trade_type == 'sell':
            return price - price * self.take_profit_coef
