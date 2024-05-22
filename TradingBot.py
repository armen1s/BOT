import time
import math
import ccxt
import pandas as pd
import logging
from config_api import API_KEY, API_SECRET
from config_trading import SYMBOL, LEVERAGE, POSITION_SIZE, FRAME, ATR_PERIOD, ATR_MULTIPLIER
from strategy import Strategy
from sl import SL

class TradingBot:
    def __init__(self):
        # Получение API ключа и секрета из конфигурации
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        # Установка символа для торговли (например, BTC/USDT)
        self.symbol = SYMBOL
        # Установка ливмента (например, 50x)
        self.leverage = LEVERAGE
        # Установка размера позиции (например, 10 USDT)
        self.position_size = POSITION_SIZE
        # Установка временного интервала для получения данных с рынка (например, '1h')
        self.frame = FRAME
        # Установка периода для вычисления ATR (например, 14)
        self.atr_period = ATR_PERIOD
        # Установка коэффициента умножения ATR (например, 3)
        self.atr_multiplier = ATR_MULTIPLIER
        # Инициализация логгера
        self.logger = logging.getLogger(__name__)
        # Установка уровня логирования на WARNING для основного логирования
        self.logger.setLevel(logging.WARNING)
        # Подключение к API биржи
        self.exchange = ccxt.bybit({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'enableRateLimit': True,
            'timeout': 10000,
            'rateLimit': 500,
            'enableLastResponseHeaders': True,
            'handleErrors': True,
            'handleHttpErrors': True,
            'keepAlive': False,
            'retry': 0,
            'verbose': False,
            'urls': {
                'api': {
                    'spot': 'https://api.bybit.com',
                    'linear': 'https://api.bybit.com',
                    'linear_usdt': 'https://api.bybit.com',
                    'api_linear': 'https://api.bybit.com',
                    'api_linear_usdt': 'https://api.bybit.com',
                },
                'www': 'https://www.bybit.com',
            },
        })
        # Установка уровня ливмента
        self.exchange.set_leverage(self.symbol, self.leverage)
        # Установка стратегии для торговли
        self.strategy = Strategy(self.exchange, self.symbol, self.leverage, self.position_size, self.frame, self.atr_period, self.atr_multiplier)
        # Установка стоп-лосса для торговли
        self.sl = SL(is_dinamic=True, coef=0.25)

    def get_ticker(self):
        # Получение текущей цены символа
        ticker = self.exchange.fetch_ticker(self.symbol)
        return ticker

    def get_order_book(self):
        # Получение книги заявок для символа
        order_book = self.exchange.fetch_order_book(self.symbol)
        return order_book

    def get_trades(self):
        # Получение сделок для символа
        trades = self.exchange.fetch_trades(self.symbol)
        return trades

    def get_kline(self, timeframe: str):
        # Получение свечей для символа с заданным временным интервалом
        kline = self.exchange.fetch_ohlcv(self.symbol, timeframe)
        return kline

    def trade(self):
        # Определение типа сделки
        trade_type = self.strategy.get_trade_type()
        if trade_type is not None:
            # Определение размера сделки
            position_size = self.strategy.get_position_size()
            # Выставление стоп-лосса
            stop_loss = self.sl.get_sl(self.strategy.get_ohlcv(), trade_type)
            # Выставление сделки
            self.exchange.create_order(self.symbol, 'limit', trade_type, position_size, stop_loss_price=stop_loss)
            self.logger.warning('Сделка выполнена: type=%s, size=%s, stop_loss=%s', trade_type, position_size, stop_loss)

    def run(self):
        # Выполнение сделок бесконечно
        while True:
            # Ожидание перед следующей итерацией
            time.sleep(60)
            # Выполнение сделки
            self.trade()
