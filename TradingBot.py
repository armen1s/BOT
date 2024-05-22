import time
import math
import ccxt
import pandas as pd
import logging
from config_api import API_KEY, API_SECRET
from config_trading import SYMBOL, LEVERAGE, POSITION_SIZE, FRAME
from strategy import Strategy

class TradingBot:
    def __init__(self):
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.symbol = SYMBOL
        self.leverage = LEVERAGE
        self.position_size = POSITION_SIZE
        self.frame = FRAME
        self.exchange = ccxt.binance({'apiKey': self.api_key, 'secret': self.api_secret})
        self.logger = logging.getLogger(__name__)
        self.strategy = Strategy(self.exchange, self.symbol, self.leverage, self.position_size, self.frame)

    def get_kline(self, frame):
        ohlcv = self.exchange.fetch_ohlcv(self.symbol, frame)
        return ohlcv

    def trade(self):
        trade_type = self.strategy.get_trade_type(self.get_kline(self.frame))
        if trade_type is not None:
            position_size = self.strategy.get_position_size()
            stop_loss_price = self.strategy.get_stop_loss(self.get_kline(self.frame), trade_type)
            self.exchange.create_order(self.symbol, 'limit', trade_type, position_size, stop_loss_price=stop_loss_price)
            self.logger.warning('Сделка выполнена: type=%s, size=%s, stop_loss=%s', trade_type, position_size, stop_loss_price)

    def run(self):
        while True:
            time.sleep(60)
            self.trade()
