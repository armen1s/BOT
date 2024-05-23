# strategy.py

import pandas as pd
from sl import SL
from talib import RSI
import asyncio
import logging

logger = logging.getLogger(name)

class Strategy:
    def init(self, exchange, symbol, leverage, position_size, frame, take_profit_coef):
        self.exchange = exchange
        self.symbol = symbol
        self.leverage = leverage
        self.position_size = position_size
        self.frame = frame
        self.sl = SL(is_dynamic=True, coef=0.25)
        self.take_profit_coef = take_profit_coef

    async def get_rsi(self, kline):
        close_prices = [x[4] for x in kline]
        loop = asyncio.get_event_loop()
        rsi = await loop.run_in_executor(None, RSI, close_prices, 2)
        logger.debug(f"Calculated RSI: {rsi[-1]}")
        return rsi[-1]

    async def get_trade_type(self, kline):
        rsi = await self.get_rsi(kline)
        if rsi < 35:
            trade_type = 'buy'
        elif rsi > 55:
            trade_type = 'sell'
        else:
            trade_type = None
        logger.debug(f"Determined trade type: {trade_type}")
        return trade_type

    def get_position_size(self):
        logger.debug(f"Position size: {self.position_size}")
        return self.position_size

    async def get_stop_loss(self, kline, trade_type):
        df = pd.DataFrame(kline, columns=['open', 'high', 'low', 'close', 'volume'])
        stop_loss = await self.sl.calculate_sl(df, trade_type)
        logger.debug(f"Calculated stop loss: {stop_loss}")
        return stop_loss

    async def get_take_profit(self, kline, trade_type):
        price = kline[-1][4]  # последняя цена закрытия
        if trade_type == 'buy':
            take_profit = price + price * self.take_profit_coef
        elif trade_type == 'sell':
            take_profit = price - price * self.take_profit_coef
        logger.debug(f"Calculated take profit: {take_profit}")
        return take_profit

    async def execute_trade(self):
        kline = await self.exchange.fetch_ohlcv(self.symbol, timeframe=self.frame)
        trade_type = await self.get_trade_type(kline)
        
        if trade_type:
            position_size = self.get_position_size()
            stop_loss = await self.get_stop_loss(kline, trade_type)
            take_profit = await self.get_take_profit(kline, trade_type)
            
            try:
                # Открытие позиции с использованием API биржи
                order = await self.exchange.create_order(
                    symbol=self.symbol,
                    type='market',
                    side=trade_type,
                    amount=position_size,
                    params={
                        'stop_loss': stop_loss,
                        'take_profit': take_profit
                    }
                )
                logger.info(f"Opened {trade_type} position for {self.symbol} with size {position_size}")
                return order
            except Exception as e:
                logger.error(f"Error executing trade: {e}", exc_info=True)
        else:
            logger.debug("No trade action taken")

# Пример использования
# exchange = ... # Инициализация объекта биржи
# strategy = Strategy(exchange, SYMBOL, LEVERAGE, POSITION_SIZE, FRAME, TAKE_PROFIT_COEF)
# asyncio.run(strategy.execute_trade())
