import pandas as pd
import numpy as np
from sl import SL
from talib import RSI

class Strategy:
    def __init__(self, symbol, leverage, position_size, frame, take_profit_coef):
        """
        Инициализация стратегии.

        Args:
        symbol (str): Торговая пара.
        leverage (float): Плечо.
        position_size (float): Размер позиции.
        frame (str): Таймфрейм для анализа.
        take_profit_coef (float): Коэффициент тейк-профита.
        """
        self.symbol = symbol
        self.leverage = leverage
        self.position_size = position_size
        self.frame = frame
        self.sl = SL(is_dynamic=True, coef=0.25)
        self.take_profit_coef = take_profit_coef

    def get_rsi(self, kline):
        """
        Рассчитывает RSI на основе предоставленных данных.

        Args:
        kline (list): Список свечей.

        Returns:
        float: Значение RSI.
        """
        close_prices = np.array([x[4] for x in kline], dtype=np.float64)
        rsi = RSI(close_prices, timeperiod=2)
        return rsi[-1]

    def get_trade_type(self, kline):
        """
        Определяет тип сделки на основе RSI.

        Args:
        kline (list): Список свечей.

        Returns:
        str: Тип сделки ('buy' или 'sell').
        """
        rsi = self.get_rsi(kline)
        if rsi < 35:
            return 'buy'
        elif rsi > 55:
            return 'sell'
        else:
            return None

    def get_position_size(self):
        """
        Возвращает размер позиции.

        Returns:
        float: Размер позиции.
        """
        return self.position_size

    def get_stop_loss(self, kline, trade_type):
        """
        Рассчитывает уровень стоп-лосса.

        Args:
        kline (list): Список свечей.
        trade_type (str): Тип сделки ('buy' или 'sell').

        Returns:
        float: Уровень стоп-лосса.
        """
        df = pd.DataFrame(kline, columns=['open', 'high', 'low', 'close', 'volume'])
        return self.sl.calculate_sl(df, trade_type)

    def get_take_profit(self, kline, trade_type):
        """
        Рассчитывает уровень тейк-профита.

        Args:
        kline (list): Список свечей.
        trade_type (str): Тип сделки ('buy' или 'sell').

        Returns:
        float: Уровень тейк-профита.
        """
        price = kline[-1][4]
        if trade_type == 'buy':
            return price + price * self.take_profit_coef
        elif trade_type == 'sell':
            return price - price * self.take_profit_coef
