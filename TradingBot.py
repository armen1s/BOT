import time
import math
import ccxt
import pandas as pd
import logging
from config_api import API_KEY, API_SECRET
from config_trading import SYMBOL, LEVERAGE, POSITION_SIZE, FRAME
from sl import SL

class TradingBot:
    def __init__(self):
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.symbol = SYMBOL
        self.leverage = LEVERAGE
        self.position_size = POSITION_SIZE
        self.frame = FRAME
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.WARNING)
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
        self.exchange.set_leverage(self.symbol, self.leverage)
        self.strategy = Strategy(self.exchange, self.symbol, self.leverage, self.position_size, self.frame)
        self.sl = SL(is_dinamic=True, coef=0.25)

    def get_ticker(self):
        ticker = self.exchange.fetch_ticker(self.symbol)
        return ticker

    def get_order_book(self):
        order_book = self.exchange.fetch_order_book(self.symbol)
        return order_book

    def get_trades(self):
        trades = self.exchange.fetch_trades(self.symbol)
        return trades

    def get_kline(self, timeframe: str):
        kline = self.exchange.fetch_ohlcv(self.symbol, timeframe)
        return kline

    def trade(self):
        trade_type = self.strategy.get_trade_type()
        if trade_type is not None:
            position_size = self.strategy.get_position_size()
            stop_loss_price = self.sl.get_sl(self.get_kline(self.frame), trade_type)
            self.exchange.create_order(self.symbol, 'limit', trade_type, position_size, stop_loss_price=stop_loss_price)
            self.logger.warning('Сделка выполнена: type=%s, size=%s, stop_loss=%s', trade_type, position_size, stop_loss_price)

    def run(self):
        while True:
            time.sleep(60)
            self.trade()
