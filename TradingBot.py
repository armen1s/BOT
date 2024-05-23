# TradingBot.py

import time
import ccxt
import pandas as pd
import logging
from config_api import API_KEY, API_SECRET
from config_trading import SYMBOL, LEVERAGE, POSITION_SIZE, FRAME, TAKE_PROFIT_COEF, DYNAMIC_SL_INTERVAL
from strategy import Strategy

class TradingBot:
    def init(self):
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.symbol = SYMBOL
        self.leverage = LEVERAGE
        self.position_size = POSITION_SIZE
        self.frame = FRAME
        self.dynamic_sl_interval = DYNAMIC_SL_INTERVAL
        self.exchange = ccxt.bybit({'apiKey': self.api_key, 'secret': self.api_secret})
        self.logger = logging.getLogger(name)
        self.strategy = Strategy(self.exchange, self.symbol, self.leverage, self.position_size, self.frame, TAKE_PROFIT_COEF)
        self.current_order = None

    def get_kline(self, frame):
        try:
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, frame)
            return ohlcv
        except Exception as e:
            self.logger.error('Ошибка при получении данных OHLCV: %s', str(e))
            return []

    def trade(self):
        try:
            kline = self.get_kline(self.frame)
            if not kline:
                return
            trade_type = self.strategy.get_trade_type(kline)
            if trade_type is not None:
                position_size = self.strategy.get_position_size()
                stop_loss_price = self.strategy.get_stop_loss(kline, trade_type)
                take_profit_price = self.strategy.get_take_profit(kline, trade_type)
                order = self.exchange.create_order(self.symbol, 'limit', trade_type, position_size, {
                    'stop_loss': stop_loss_price,
                    'take_profit': take_profit_price
                })
                self.current_order = order
                self.logger.info('Сделка выполнена: type=%s, size=%s, stop_loss=%s, take_profit=%s, order_id=%s',
                                 trade_type, position_size, stop_loss_price, take_profit_price, order['id'])
            else:
                self.logger.info('Нет подходящей сделки.')
        except Exception as e:
            self.logger.error('Ошибка при выполнении сделки: %s', str(e))

    def update_stop_loss(self):
        try:
            if self.current_order:
                kline = self.get_kline(self.frame)
                if not kline:
                    return
                trade_type = 'buy' if self.current_order['side'] == 'buy' else 'sell'
                new_stop_loss = self.strategy.get_stop_loss(kline, trade_type)
                self.exchange.update_order(self.current_order['id'], {'stop_loss': new_stop_loss})
                self.logger.info('Обновление стоп-лосса: order_id=%s, new_stop_loss=%s', self.current_order['id'], new_stop_loss)
        except Exception as e:
            self.logger.error('Ошибка при обновлении стоп-лосса: %s', str(e))

    def run(self):
        last_sl_update = time.time()
        while True:
            self.trade()
            if time.time() - last_sl_update >= self.dynamic_sl_interval:
                self.update_stop_loss()
                last_sl_update = time.time()
            time.sleep(60)
