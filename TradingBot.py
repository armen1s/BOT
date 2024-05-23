# TradingBot.py

import asyncio
import logging
from config_api import API_KEY, API_SECRET
from trading_config import SYMBOL, LEVERAGE, POSITION_SIZE, FRAME, TAKE_PROFIT_COEF, DYNAMIC_SL_INTERVAL, logger
from strategy import Strategy
from bybit import Bybit  # Предположим, что Bybit - это класс, реализующий взаимодействие с API Bybit

class TradingBot:
    def init(self, api_key, api_secret, symbol, leverage, position_size, frame, take_profit_coef, sl_interval):
        self.exchange = Bybit(api_key, api_secret)
        self.strategy = Strategy(self.exchange, symbol, leverage, position_size, frame, take_profit_coef)
        self.sl_interval = sl_interval
        self.is_running = False

    async def start(self):
        self.is_running = True
        logger.info("Trading bot started.")
        while self.is_running:
            try:
                await self.strategy.execute_trade()
                await asyncio.sleep(self.sl_interval)
            except Exception as e:
                logger.error(f"Error in trading loop: {e}", exc_info=True)

    async def stop(self):
        self.is_running = False
        await self.exchange.close()
        logger.info("Trading bot stopped.")

    async def run(self):
        await self.start()

def main():
    bot = TradingBot(
        api_key=API_KEY,
        api_secret=API_SECRET,
        symbol=SYMBOL,
        leverage=LEVERAGE,
        position_size=POSITION_SIZE,
        frame=FRAME,
        take_profit_coef=TAKE_PROFIT_COEF,
        sl_interval=DYNAMIC_SL_INTERVAL
    )
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        asyncio.run(bot.stop())

if name == "main":
    main()
